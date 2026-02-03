"""
Agent协调器 - 管理多个Agent的协作执行
"""
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from agents import SourceAnalyzer, Translator, Reviewer, Optimizer, BaseAgent
from models import TranslationContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str
    enabled: bool = True
    order: int = 0
    retry_count: int = 2
    dependencies: List[str] = field(default_factory=list)


class AgentOrchestrator:
    """
    Agent协调器
    
    负责：
    1. 管理所有Agent的生命周期
    2. 协调Agent执行顺序
    3. 处理Agent间的数据传递
    4. 管理重试逻辑
    5. 提供执行进度回调
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化协调器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        
        # 进度回调
        self.progress_callbacks: List[Callable[[str, str, Any], None]] = []
        
        # 停止标志
        self._stop_requested = False
        
        # 初始化Agent
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有Agent"""
        agent_mapping = {
            'source_analyzer': SourceAnalyzer,
            'translator': Translator,
            'reviewer': Reviewer,
            'optimizer': Optimizer
        }
        
        # 从配置中读取Agent配置（支持 agents_config 或 agents 两种路径）
        agents_config = self.config.get('agents_config', {}) or self.config.get('agents', {})
        
        for agent_key, agent_class in agent_mapping.items():
            agent_cfg = agents_config.get(agent_key, {})
            
            if agent_cfg.get('enabled', True):
                try:
                    # 创建Agent实例
                    self.agents[agent_key] = agent_class(self.config)
                    
                    # 保存配置
                    self.agent_configs[agent_key] = AgentConfig(
                        name=agent_class.name,
                        enabled=True,
                        order=agent_cfg.get('order', 0),
                        retry_count=agent_cfg.get('retry_count', 2)
                    )
                    
                    logger.info(f"Agent '{agent_class.name}' 初始化成功")
                    
                except Exception as e:
                    logger.error(f"Agent '{agent_class.name}' 初始化失败: {e}")
    
    def register_progress_callback(self, callback: Callable[[str, str, Any], None]):
        """
        注册进度回调函数
        
        Args:
            callback: 回调函数，参数为(stage, status, data)
        """
        # 防止重复注册相同的回调函数
        if callback not in self.progress_callbacks:
            self.progress_callbacks.append(callback)
    
    def clear_progress_callbacks(self):
        """清空所有进度回调函数"""
        self.progress_callbacks.clear()
    
    def _notify_progress(self, stage: str, status: str, data: Any = None):
        """通知所有回调函数"""
        for callback in self.progress_callbacks:
            try:
                callback(stage, status, data)
            except Exception as e:
                logger.warning(f"进度回调执行失败: {e}")
    
    def execute_single(self, agent_key: str, context: TranslationContext, stage_key: str = None) -> Optional[AgentResult]:
        """
        执行单个Agent
        
        Args:
            agent_key: Agent标识
            context: 翻译上下文
            stage_key: 用于进度通知的阶段标识（默认为agent_key）
            
        Returns:
            Agent执行结果
        """
        agent = self.agents.get(agent_key)
        if not agent:
            logger.warning(f"Agent '{agent_key}' 不存在或未启用")
            return None
        
        # 使用stage_key进行进度通知（如果提供）
        notify_key = stage_key if stage_key else agent_key
        
        config = self.agent_configs.get(agent_key)
        max_retries = config.retry_count if config else 2
        
        # 通知开始
        self._notify_progress(notify_key, 'started', {'agent_name': agent.name})
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[{agent.name}] 执行尝试 {attempt + 1}/{max_retries + 1}")
                result = agent.execute(context)
                
                # 通知完成
                self._notify_progress(
                    notify_key, 
                    'completed', 
                    {
                        'agent_name': agent.name,
                        'status': result.status.value,
                        'result': result
                    }
                )
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"[{agent.name}] 执行失败 (尝试 {attempt + 1}): {e}")
                
                if attempt < max_retries:
                    self._notify_progress(
                        notify_key,
                        'retrying',
                        {'attempt': attempt + 1, 'max_retries': max_retries}
                    )
        
        # 所有重试都失败
        logger.error(f"[{agent.name}] 执行失败，已重试{max_retries}次")
        
        failed_result = AgentResult(
            agent_name=agent.name,
            status=AgentStatus.FAILED,
            error=str(last_error)
        )
        
        self._notify_progress(
            notify_key,
            'failed',
            {'agent_name': agent.name, 'error': str(last_error)}
        )
        
        return failed_result
    
    def execute_pipeline(self, context: TranslationContext) -> TranslationContext:
        """
        执行完整翻译流水线（非迭代模式）
        
        检查点：每个阶段开始前会检查停止请求。
        
        流程：分析 → 翻译 → 译后审核 → 智能路由 → 优化 → 输出
        
        智能路由逻辑：
        - 审核优秀(≥90分)：跳过优化直接输出
        - 审核通过(80-89分)：进入正常优化流程
        - 审核未通过(<80分)：尝试修复，记录警告
        
        注：非迭代模式下不返回重试，但会根据审核结果调整优化策略
        
        Args:
            context: 翻译上下文
            
        Returns:
            更新后的翻译上下文
        """
        logger.info("开始翻译流水线")
        self._notify_progress('pipeline', 'started', {'source': context.source_text[:100], 'mode': 'pipeline'})
        
        # 输入阶段已完成（用户已提供输入）
        self._notify_progress('input', 'completed', {'message': '用户输入已接收'})
        
        # ========== 阶段1: 原语言分析 ==========
        self._check_stop_requested()
        if 'source_analyzer' in self.agents:
            context.update_stage('source_analyzer')
            result = self.execute_single('source_analyzer', context)
            if result is None or result.status == AgentStatus.FAILED:
                logger.error("原语言分析失败")
                context.update_stage('failed')
                return context
        
        # ========== 阶段2: 翻译 ==========
        self._check_stop_requested()
        if 'translator' in self.agents:
            context.update_stage('translator')
            result = self.execute_single('translator', context)
            if result is None or result.status == AgentStatus.FAILED:
                logger.error("翻译失败")
                context.update_stage('failed')
                return context
        
        # ========== 阶段3: 译后审核 ==========
        self._check_stop_requested()
        review_passed = False
        review_result = None
        if 'reviewer' in self.agents:
            context.update_stage('reviewer')
            review_result = self.execute_single('reviewer', context, stage_key='reviewer')
            if review_result is None or review_result.status == AgentStatus.FAILED:
                logger.error("译后审核失败")
                context.update_stage('failed')
                return context
            
            review_passed = self._check_review_passed(review_result)
            score = review_result.score if hasattr(review_result, 'score') else 0
            severity = self._get_review_severity(review_result)
            
            if review_passed:
                if score >= 90:
                    # 高分（≥90分）：译文优秀，跳过优化直接输出
                    logger.info(f"译后审核评分优秀（{score}分），跳过优化和优化后审核直接输出")
                    self._notify_progress('flow_control', 'skip_stage', {
                        'from': 'reviewer',
                        'skipped_stages': ['optimizer', 'reviewer2'],
                        'reason': f'译后审核评分优秀（{score}分），译文质量已达标，无需优化',
                        'final_score': score
                    })
                    # 标记跳过的阶段
                    self._notify_progress('optimizer', 'skipped', {'reason': '评分优秀，跳过'})
                    self._notify_progress('reviewer2', 'skipped', {'reason': '评分优秀，跳过'})
                    # 直接完成
                    context.complete()
                    self._notify_progress('output', 'completed', {'message': '翻译完成', 'skipped': True, 'reason': '评分优秀'})
                    self._notify_progress('pipeline', 'completed', {
                        'final_translation': context.get_final_translation(),
                        'skipped_stages': ['optimizer', 'reviewer2']
                    })
                    return context
                else:
                    logger.info(f"译后审核通过（评分: {score}），进入优化阶段")
            elif severity == 'minor':
                logger.info(f"译后审核小问题（评分: {score}，80-89分），优化专家将尝试修复")
            else:
                logger.warning(f"译后审核大问题（评分: {score}，<80分），译文质量可能不佳")
        
        # ========== 阶段4: 优化（智能模式） ==========
        self._check_stop_requested()
        if 'optimizer' in self.agents:
            context.update_stage('optimizer')
            
            # 根据审核结果设置优化模式
            if review_result and not review_passed and severity == 'minor':
                # 小问题，使用修复模式
                context._fix_mode = True
                logger.info("优化专家进入修复模式")
            
            opt_result = self.execute_single('optimizer', context)
            
            # 清除修复模式标记
            if hasattr(context, '_fix_mode'):
                delattr(context, '_fix_mode')
            
            if opt_result is None or opt_result.status == AgentStatus.FAILED:
                logger.warning("优化失败，使用当前译文")
            else:
                # ========== 阶段5: 优化后完整审核 ==========
                context.update_stage('reviewer2')
                self._notify_progress('reviewer2', 'started', {'message': '优化后进行完整审核'})
                
                review2_result = self._perform_post_opt_review(context)
                
                if review2_result is None:
                    logger.warning("优化后审核未执行")
                elif review2_result.status == AgentStatus.FAILED:
                    logger.warning("优化后审核失败")
                else:
                    score2 = review2_result.score if hasattr(review2_result, 'score') else 0
                    passed2 = self._check_review_passed(review2_result)
                    
                    if passed2:
                        logger.info(f"优化后审核通过（评分: {score2}）")
                        self._notify_progress('reviewer2', 'completed', {
                            'passed': True,
                            'score': score2,
                            'message': '优化后审核通过'
                        })
                    else:
                        logger.warning(f"优化后审核未通过（评分: {score2}）")
                        self._notify_progress('reviewer2', 'completed', {
                            'passed': False,
                            'score': score2,
                            'message': '优化后审核未通过（非迭代模式继续）'
                        })
        
        # 完成前检查停止请求
        self._check_stop_requested()
        context.complete()
        
        # 输出阶段完成
        self._notify_progress('output', 'completed', {'message': '翻译完成'})
        
        self._notify_progress('pipeline', 'completed', {
            'final_translation': context.get_final_translation()
        })
        
        return context
    
    def execute_iterative(self, context: TranslationContext) -> TranslationContext:
        """
        执行迭代式翻译流程（优化版）
        
        改进流程：
        分析 → 翻译 → 译后审核 ──优秀(≥90分)──→ 直接输出
                      │不通过
                      ↓
               判断问题严重程度
                      │
            ┌─────────┴─────────┐
            ↓                   ↓
        小问题(80-89)        大问题(<80)
            │                   │
            ↓                   ↓
        优化专家修复        返回翻译专家
        （修复模式）        重新翻译
            │
            ↓（审核通过）
          优化 → 输出
            │
            └─未通过→ 返回翻译专家
        
        规则：
        1. 译后审核≥90分：译文优秀，跳过优化和审核直接输出
        2. 译后审核80-89分：进入正常优化流程，优化后需经审核
        3. 译后审核<80分：返回翻译专家重新翻译
        4. 修复模式后审核未通过：返回翻译专家重新翻译
        5. 正常优化后的润色不强制要求审核
        
        Args:
            context: 翻译上下文
            
        Returns:
            更新后的翻译上下文
        """
        logger.info("开始迭代式翻译流程（优化版）")
        self._notify_progress('pipeline', 'started', {'iterative': True, 'version': 'optimized'})
        
        # 输入阶段已完成（用户已提供输入）
        self._notify_progress('input', 'completed', {'message': '用户输入已接收'})
        
        # 第一轮：分析
        context.update_stage('source_analyzer')
        self.execute_single('source_analyzer', context)
        
        max_iterations = context.max_iterations
        current_stage = 'translator'  # 当前所在阶段：translator 或 optimizer
        
        for iteration in range(max_iterations):
            # 检查停止请求
            self._check_stop_requested()
            
            logger.info(f"=== 迭代轮次 {iteration + 1}/{max_iterations} ===")
            context.iteration_count = iteration + 1
            
            self._notify_progress('iteration', 'started', {
                'iteration': iteration + 1,
                'max_iterations': max_iterations
            })
            
            # ========== 阶段1: 翻译 ==========
            self._check_stop_requested()
            if current_stage == 'translator':
                context.update_stage('translator')
                
                if iteration > 0:
                    # 从审核返回，需要告知原因
                    return_reason = self._get_last_review_feedback(context, 'translator')
                    self._notify_progress('flow_control', 'return_to_agent', {
                        'from': 'reviewer',
                        'to': 'translator',
                        'reason': f'审核未通过，返回翻译专家重新翻译。原因：{return_reason}'
                    })
                
                trans_result = self.execute_single('translator', context)
                
                if trans_result is None or trans_result.status == AgentStatus.FAILED:
                    logger.error("翻译失败，终止迭代")
                    break
                
                # 翻译后进行审核
                context.update_stage('reviewer')
                review_result = self.execute_single('reviewer', context, stage_key='reviewer')
                
                if review_result is None:
                    logger.error("审核失败")
                    break
                
                # 记录审核结果
                context.review_result = review_result
                score = review_result.score if hasattr(review_result, 'score') else 0
                passed = self._check_review_passed(review_result)
                severity = self._get_review_severity(review_result)
                
                if passed:
                    # 审核通过（≥85分）
                    if score >= 90:
                        # 高分（≥90分）：译文优秀，跳过优化直接输出
                        logger.info(f"译后审核评分优秀（{score}分），跳过优化直接输出")
                        self._notify_progress('flow_control', 'skip_stage', {
                            'from': 'reviewer',
                            'skipped_stages': ['optimizer', 'reviewer2'],
                            'reason': f'译后审核评分优秀（{score}分），译文质量已达标，无需优化',
                            'final_score': score
                        })
                        # 标记跳过的阶段为SKIPPED状态
                        self._notify_progress('optimizer', 'skipped', {'reason': '评分优秀，跳过'})
                        self._notify_progress('reviewer2', 'skipped', {'reason': '评分优秀，跳过'})
                        break
                    else:
                        # 良好（80-89分）：进入优化流程
                        logger.info(f"译后审核通过（评分: {score}），进入优化阶段")
                        current_stage = 'optimizer'
                        continue
                
                # 审核未通过，判断问题严重程度
                logger.info(f"译后审核未通过（评分: {score}，严重程度: {severity}）")
                
                # 检查是否达到最大迭代次数
                if iteration == max_iterations - 1:
                    logger.warning("已达最大迭代次数且审核未通过，流程结束")
                    break
                
                if severity == 'minor':
                    # 小问题(80-89分)：尝试让优化专家修复
                    logger.info("问题较小，尝试让优化专家修复")
                    self._notify_progress('flow_control', 'smart_routing', {
                        'from': 'reviewer',
                        'to': 'optimizer',
                        'mode': 'fix_mode',
                        'reason': f'审核评分{score}分，问题较小，尝试优化修复而非重新翻译'
                    })
                    
                    # 进入修复模式
                    fix_result = self._execute_fix_mode(context, review_result)
                    
                    if fix_result:
                        # 修复成功，进入优化阶段（正常润色）
                        current_stage = 'optimizer'
                        continue
                    else:
                        # 修复失败，返回翻译阶段
                        logger.info("优化专家修复未能解决问题，返回翻译专家")
                        current_stage = 'translator'
                        continue
                else:
                    # 大问题(<80分)：返回翻译专家重新翻译
                    logger.info("问题严重，返回翻译专家重新翻译")
                    self._notify_progress('flow_control', 'return_to_agent', {
                        'from': 'reviewer',
                        'to': 'translator',
                        'reason': f'译后审核未通过（评分{score}），问题较严重，需要重新翻译。原因：{self._get_review_failure_reason(review_result)}'
                    })
                    current_stage = 'translator'
                    continue
            
            # ========== 阶段2: 优化（正常润色） ==========
            elif current_stage == 'optimizer':
                self._check_stop_requested()
                context.update_stage('optimizer')
                
                # 判断是修复模式还是正常润色模式
                is_fix_mode = hasattr(context, '_fix_mode') and context._fix_mode
                
                opt_result = self.execute_single('optimizer', context)
                
                if opt_result is None or opt_result.status == AgentStatus.FAILED:
                    logger.warning("优化失败，使用当前译文")
                    break
                
                # ========== 阶段3: 优化后完整审核 ==========
                context.update_stage('reviewer2')
                self._notify_progress('reviewer2', 'started', {'message': '优化后进行完整审核'})
                
                review2_result = self._perform_post_opt_review(context)
                
                if review2_result is None:
                    logger.warning("优化后审核未执行，流程结束")
                    break
                
                score2 = review2_result.score if hasattr(review2_result, 'score') else 0
                passed2 = self._check_review_passed(review2_result)
                
                if passed2:
                    logger.info(f"优化后审核通过（评分: {score2}），翻译流程结束")
                    self._notify_progress('reviewer2', 'completed', {
                        'passed': True,
                        'score': score2,
                        'message': '优化后审核通过'
                    })
                    break
                else:
                    # 审核未通过
                    logger.info(f"优化后审核未通过（评分: {score2}）")
                    self._notify_progress('reviewer2', 'completed', {
                        'passed': False,
                        'score': score2,
                        'message': '优化后审核未通过'
                    })
                    
                    # 检查是否还有迭代次数
                    if iteration == max_iterations - 1:
                        logger.warning("优化后审核未通过，但已达最大迭代次数，流程结束")
                        break
                    
                    # 返回优化阶段继续优化
                    logger.info("返回优化阶段继续优化")
                    self._notify_progress('flow_control', 'return_to_agent', {
                        'from': 'reviewer2',
                        'to': 'optimizer',
                        'reason': f'优化后审核未通过（评分{score2}），需要继续优化'
                    })
                    current_stage = 'optimizer'
                    continue
        
        context.complete()
        
        # 输出阶段完成
        self._notify_progress('output', 'completed', {'message': '翻译完成'})
        
        self._notify_progress('pipeline', 'completed', {
            'iterations': context.iteration_count,
            'final_translation': context.get_final_translation()
        })
        
        return context
    
    def _get_review_severity(self, review_result) -> str:
        """
        判断审核问题的严重程度
        
        Returns:
            'minor': 小问题（70-84分）
            'major': 大问题（<70分）
        """
        if review_result is None:
            return 'major'
        
        score = review_result.score if hasattr(review_result, 'score') else 0
        
        if score >= 80:
            return 'minor'
        else:
            return 'major'
    
    def _execute_fix_mode(self, context: TranslationContext, review_result) -> bool:
        """
        执行修复模式：让优化专家修复审核发现的问题，修复后需经审核专家审核
        
        Args:
            context: 翻译上下文
            review_result: 审核结果
            
        Returns:
            True: 修复成功且审核通过
            False: 修复失败或审核未通过（需要重新翻译）
        """
        logger.info("进入修复模式：优化专家针对性修复问题")
        
        # 标记修复模式
        context._fix_mode = True
        
        # 执行优化（修复模式）
        opt_result = self.execute_single('optimizer', context)
        
        # 清除修复模式标记
        context._fix_mode = False
        
        if opt_result is None or opt_result.status == AgentStatus.FAILED:
            logger.warning("优化专家修复失败")
            return False
        
        # 修复完成后必须经过审核专家审核
        logger.info("修复完成，进入修复后审核")
        fix_review_result = self.execute_single('reviewer', context, stage_key='reviewer_fix')
        
        if fix_review_result is None or fix_review_result.status == AgentStatus.FAILED:
            logger.warning("修复后审核失败")
            return False
        
        # 检查审核是否通过
        fix_passed = self._check_review_passed(fix_review_result)
        fix_score = fix_review_result.score if hasattr(fix_review_result, 'score') else 0
        
        if fix_passed:
            logger.info(f"修复后审核通过（评分: {fix_score}）")
            # 更新审核结果为通过状态
            if context.review_result and hasattr(context.review_result, 'passed'):
                context.review_result.passed = True
            return True
        else:
            logger.warning(f"修复后审核未通过（评分: {fix_score}），需要重新翻译")
            self._notify_progress('reviewer_fix', 'failed', {
                'score': fix_score,
                'message': '修复后审核未通过'
            })
            return False
    
    def _perform_post_opt_review(self, context: TranslationContext) -> Optional[AgentResult]:
        """
        优化后的完整审核
        
        使用Reviewer Agent对优化后的译文进行完整的质量审核，
        与译后审核相同的标准和流程。
        
        Args:
            context: 翻译上下文
            
        Returns:
            ReviewResult: 审核结果，包含评分和是否通过
        """
        if 'reviewer' not in self.agents:
            logger.warning("审核专家未启用，跳过优化后审核")
            return None
        
        logger.info("执行优化后完整审核...")
        
        # 保存第一次审核结果，防止被覆盖
        saved_review1_result = context.review_result
        
        # 执行审核（使用'reviewer2'作为stage_key以区分第一次审核）
        review_result = self.execute_single('reviewer', context, stage_key='reviewer2')
        
        # 恢复第一次审核结果，将第二次审核结果存储到review2_result
        context.review_result = saved_review1_result
        if review_result:
            context.review2_result = review_result
        
        return review_result
    
    def _check_review_passed(self, review_result) -> bool:
        """检查审核是否通过"""
        if review_result is None:
            return False
        if hasattr(review_result, 'passed'):
            return review_result.passed
        return False
    
    def _get_review_failure_reason(self, review_result) -> str:
        """获取审核失败的原因"""
        if review_result is None:
            return "审核结果异常"
        
        reasons = []
        
        # 获取评分
        if hasattr(review_result, 'score'):
            reasons.append(f"评分 {review_result.score}/100 未达到通过标准")
        
        # 获取问题列表
        if hasattr(review_result, 'issues') and review_result.issues:
            issue_count = len(review_result.issues)
            reasons.append(f"发现 {issue_count} 个问题")
            
            # 列出前3个问题
            for i, issue in enumerate(review_result.issues[:3], 1):
                issue_type = issue.get('type', '问题')
                desc = issue.get('description', '')
                reasons.append(f"  {i}. [{issue_type}] {desc}")
        
        # 获取建议
        if hasattr(review_result, 'suggestions') and review_result.suggestions:
            reasons.append("主要建议:")
            for suggestion in review_result.suggestions[:2]:
                reasons.append(f"  - {suggestion}")
        
        return "；".join(reasons) if reasons else "未通过审核"
    
    def _get_last_review_feedback(self, context: TranslationContext, target_stage: str) -> str:
        """获取上轮审核的反馈信息，用于返回时通知"""
        if context.review_result is None:
            return "上轮审核未通过"
        
        return self._get_review_failure_reason(context.review_result)
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有Agent状态"""
        status = {}
        for key, agent in self.agents.items():
            status[key] = {
                'name': agent.name,
                'enabled': self.agent_configs.get(key, AgentConfig(name=key)).enabled,
                'stats': agent.get_stats()
            }
        return status
    
    def reset(self):
        """重置协调器状态"""
        # 重新初始化所有Agent
        self.agents.clear()
        self.agent_configs.clear()
        self._stop_requested = False
        self._init_agents()
    
    def request_stop(self):
        """请求停止翻译流程"""
        self._stop_requested = True
        logger.info("收到停止请求，将在下一个检查点停止")
    
    def _check_stop_requested(self):
        """检查是否收到停止请求，如果是则抛出异常"""
        if self._stop_requested:
            raise InterruptedError("翻译已被用户取消")
