"""
翻译优化专家 - 对翻译进行润色和优化
"""
import json
import re
from typing import Dict, Any, List

from .base_agent import BaseAgent
from models import AgentResult, AgentStatus, OptimizationResult, TranslationContext


class Optimizer(BaseAgent):
    """
    翻译优化专家
    
    职责：
    1. 根据审核结果进行优化
    2. 修复格式和术语问题
    3. 提升译文流畅度
    """
    
    name = "翻译优化专家"
    description = "对翻译进行润色和优化"
    
    def get_system_prompt(self, context: TranslationContext) -> str:
        """获取系统提示词"""
        
        is_fix_mode = hasattr(context, '_fix_mode') and context._fix_mode
        
        if is_fix_mode:
            base_prompt = """你是一位翻译优化专家。请修复译文中的问题。

## 修复优先级

1. **关键错误**：错译、漏译、过译
2. **格式问题**：补齐缺失的标签、占位符、特殊字符
3. **术语统一**：确保术语一致
4. **流畅度**：提升译文可读性

## 输出格式

```xml
<fix_analysis>
问题分析和修复策略
</fix_analysis>

<fixed_translation>
修复后的译文
</fixed_translation>
```

## 修复报告（JSON）

```json
{{
    "fixes_summary": {{
        "critical_fixed": 0,
        "format_tags_fixed": 0,
        "terminology_fixed": 0
    }},
    "verification_passed": true
}}
```"""
        else:
            base_prompt = """你是一位翻译优化专家。请优化译文质量。

## 优化原则

1. **准确性**：修正错译、漏译、过译
2. **格式规范**：确保所有标签、占位符、特殊字符完整
3. **术语统一**：统一术语翻译
4. **流畅度**：提升译文可读性，符合目标语言习惯

## 输出格式

```xml
<optimization_analysis>
优化分析
</optimization_analysis>

<optimized>
优化后的译文
</optimized>
```

## 优化报告（JSON）

```json
{{
    "improvements": [
        {{
            "type": "问题类型",
            "reason": "优化理由"
        }}
    ]
}}
```"""

        # 添加审核问题
        if context.review_result and context.review_result.issues:
            issues = context.review_result.issues
            review_info = "\n\n## 需修复的问题\n"
            for i, issue in enumerate(issues[:5], 1):
                review_info += f"{i}. [{issue.get('severity', '')}] {issue.get('description', '')}\n"
                review_info += f"   建议：{issue.get('suggestion', '')}\n"
            base_prompt += review_info
        
        # 添加术语信息
        if context.analysis_result and context.analysis_result.details:
            analysis = context.analysis_result.details
            key_terms = analysis.get('key_terms', [])
            if key_terms:
                base_prompt += "\n\n## 术语参考\n"
                for term_info in key_terms[:8]:
                    base_prompt += f"- {term_info.get('term', '')}：{term_info.get('translation_strategy', '')}\n"
        
        return base_prompt
    
    def process(self, context: TranslationContext) -> AgentResult:
        """执行优化"""
        source_text = context.source_text
        
        if context.optimization_result:
            translation = context.optimization_result.output
        elif context.translation_result:
            translation = context.translation_result.output
        else:
            return OptimizationResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error="没有可优化的译文"
            )
        
        is_fix_mode = hasattr(context, '_fix_mode') and context._fix_mode
        
        # 确定优化类型
        if is_fix_mode:
            opt_type = 'fix_mode'
        elif context.review_result and context.review_result.issues:
            issue_types = [issue.get('type', '') for issue in context.review_result.issues]
            if any(t in issue_types for t in ['技术规范', '格式']):
                opt_type = 'technical_fix'
            elif '术语' in issue_types:
                opt_type = 'terminology'
            elif '准确性' in issue_types:
                opt_type = 'accuracy'
            else:
                opt_type = 'general'
        else:
            opt_type = 'polish'
        
        user_content = f"""优化以下译文：

【原文】
{source_text}

【当前译文】
{translation}

类型：{opt_type}"""
        
        system_prompt = self.get_system_prompt(context)
        response = self._call_llm(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=context.temperature,
            top_p=context.top_p
        )
        
        optimized = self._extract_optimized(response, is_fix_mode)
        
        # 解析JSON
        details = {}
        improvements = []
        try:
            json_match = re.search(r'\{{[\s\S]*?\}}', response)
            if json_match:
                json_data = json.loads(json_match.group())
                details = json_data
                improvements = json_data.get('improvements', []) if not is_fix_mode else json_data.get('issues_addressed', [])
        except:
            pass
        
        result = OptimizationResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=optimized,
            optimized_translation=optimized,
            improvements=improvements,
            polish_type=opt_type,
            details=details
        )
        
        context.optimization_result = result
        return result
    
    def _extract_optimized(self, response: str, is_fix_mode: bool = False) -> str:
        """提取优化后的译文"""
        
        if is_fix_mode:
            pattern = re.compile(r"<fixed_translation>(.*?)</fixed_translation>", re.DOTALL)
            match = pattern.search(response)
            if match:
                return match.group(1).strip()
        
        pattern = re.compile(r"<optimized>(.*?)</optimized>", re.DOTALL)
        match = pattern.search(response)
        if match:
            return match.group(1).strip()
        
        # 清理分析部分
        if is_fix_mode:
            clean = re.sub(r'<fix_analysis>[\s\S]*?</fix_analysis>', '', response)
        else:
            clean = re.sub(r'<optimization_analysis>[\s\S]*?</optimization_analysis>', '', response)
        
        clean = re.sub(r'```[\s\S]*?```', '', clean).strip()
        return clean if clean else response.strip()
    
    def get_improvement_summary(self, result: OptimizationResult) -> str:
        """获取优化改进摘要"""
        improvements = result.improvements
        if not improvements:
            return "已完成优化"
        
        fixes = result.details.get('fixes_summary', {}) if result.details else {}
        summary_parts = []
        
        if result.polish_type == 'fix_mode':
            if fixes.get('critical_fixed', 0) > 0:
                summary_parts.append(f"修复{fixes['critical_fixed']}处关键错误")
        
        if fixes.get('format_tags_fixed', 0) > 0:
            summary_parts.append(f"修复{fixes['format_tags_fixed']}处格式")
        if fixes.get('terminology_unified', 0) > 0:
            summary_parts.append(f"统一{fixes['terminology_unified']}处术语")
        
        if summary_parts:
            return "；".join(summary_parts)
        
        return f"优化完成（{len(improvements)}项改进）"
