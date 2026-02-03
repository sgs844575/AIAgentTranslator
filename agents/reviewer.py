"""
翻译审核专家 - 审核翻译质量
"""
import json
import re
from typing import Dict, Any, List

from .base_agent import BaseAgent
from models import AgentResult, AgentStatus, ReviewResult, TranslationContext


class Reviewer(BaseAgent):
    """
    翻译审核专家
    
    职责：
    1. 审核译文准确性
    2. 检查格式标签和特殊字符
    3. 审核术语一致性
    4. 评估译文流畅度
    5. 给出质量评分
    """
    
    name = "翻译审核专家"
    description = "审核翻译质量"
    
    DEFAULT_PASS_THRESHOLD = 80
    DEFAULT_WARNING_THRESHOLD = 80
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.agent_config = config.get('agents_config', {}).get('reviewer', {})
        
        self.pass_threshold = self.agent_config.get('pass_threshold', self.DEFAULT_PASS_THRESHOLD)
        self.warning_threshold = self.agent_config.get('warning_threshold', self.DEFAULT_WARNING_THRESHOLD)
        
        weights = self.agent_config.get('weights', {})
        self.weight_accuracy = weights.get('accuracy', 35)
        self.weight_technical = weights.get('technical', 25)
        self.weight_terminology = weights.get('terminology', 20)
        self.weight_language = weights.get('language', 15)
        self.weight_format = weights.get('format', 5)
        
        self.check_format_tags = self.agent_config.get('check_format_tags', True)
        self.check_placeholders = self.agent_config.get('check_placeholders', True)
        self.check_special_chars = self.agent_config.get('check_special_chars', True)
        self.check_terminology = self.agent_config.get('check_terminology', True)
    
    def update_config(self, new_config: Dict[str, Any]):
        self.agent_config = new_config
        self.pass_threshold = new_config.get('pass_threshold', self.DEFAULT_PASS_THRESHOLD)
        self.warning_threshold = new_config.get('warning_threshold', self.DEFAULT_WARNING_THRESHOLD)
        
        weights = new_config.get('weights', {})
        self.weight_accuracy = weights.get('accuracy', 35)
        self.weight_technical = weights.get('technical', 25)
        self.weight_terminology = weights.get('terminology', 20)
        self.weight_language = weights.get('language', 15)
        self.weight_format = weights.get('format', 5)
        
        self.check_format_tags = new_config.get('check_format_tags', True)
        self.check_placeholders = new_config.get('check_placeholders', True)
        self.check_special_chars = new_config.get('check_special_chars', True)
        self.check_terminology = new_config.get('check_terminology', True)
    
    def get_current_config(self) -> Dict[str, Any]:
        return {
            'pass_threshold': self.pass_threshold,
            'warning_threshold': self.warning_threshold,
            'weights': {
                'accuracy': self.weight_accuracy,
                'technical': self.weight_technical,
                'terminology': self.weight_terminology,
                'language': self.weight_language,
                'format': self.weight_format
            },
            'check_format_tags': self.check_format_tags,
            'check_placeholders': self.check_placeholders,
            'check_special_chars': self.check_special_chars,
            'check_terminology': self.check_terminology
        }
    
    def get_system_prompt(self, context: TranslationContext) -> str:
        """获取系统提示词"""
        return f"""你是一位翻译审核专家。请审核译文质量，输出JSON报告。

## 审核维度（总分100）

1. **准确性（{self.weight_accuracy}分）**：意思完整、语气准确、文化处理得当
2. **技术规范（{self.weight_technical}分）**：格式标签、占位符、特殊字符完整保留
3. **术语一致性（{self.weight_terminology}分）**：术语统一、专有名词一致
4. **语言表达（{self.weight_language}分）**：语法正确、流畅自然、风格保持
5. **格式规范（{self.weight_format}分）**：换行、空格、标点正确

## 评分标准

- 90-100分：优秀
- {self.pass_threshold}-89分：良好（通过）
- 70-{self.pass_threshold-1}分：一般（需修改）
- 70分以下：不合格

## 输出格式（JSON）

```json
{{
    "score": 88,
    "passed": true,
    "accuracy_score": 33,
    "technical_score": 23,
    "terminology_score": 18,
    "language_score": 12,
    "format_score": 4,
    "issues": [
        {{
            "type": "问题类型",
            "severity": "严重/中等/轻微",
            "description": "问题描述",
            "suggestion": "修改建议"
        }}
    ],
    "summary": "总体评价"
}}
```"""

    def process(self, context: TranslationContext) -> AgentResult:
        """执行审核"""
        source_text = context.source_text
        
        if context.translation_result:
            translation = context.translation_result.output
        elif context.optimization_result:
            translation = context.optimization_result.output
        else:
            return ReviewResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error="没有可审核的译文",
                passed=False
            )
        
        user_content = f"""审核以下翻译：

【原文】
{source_text}

【译文】
{translation}"""
        
        system_prompt = self.get_system_prompt(context)
        response = self._call_llm(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.2,
            top_p=0.1
        )
        
        try:
            json_match = re.search(r'\{{[\s\S]*\}}', response)
            if json_match:
                review_data = json.loads(json_match.group())
            else:
                review_data = json.loads(response)
            
            score = review_data.get('score', 0)
            passed = review_data.get('passed', score >= self.pass_threshold)
            issues = review_data.get('issues', [])
            
            result = ReviewResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                output=f"评分: {score}/100, 结果: {'通过' if passed else '未通过'}",
                score=score,
                issues=issues,
                passed=passed,
                suggestions=[issue.get('suggestion', '') for issue in issues],
                details=review_data
            )
            
            context.review_result = result
            context.iteration_count += 1
            
            return result
            
        except json.JSONDecodeError as e:
            score = self._extract_score(response)
            passed = score >= self.pass_threshold
            
            return ReviewResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                output=response,
                score=score,
                issues=[],
                passed=passed,
                error=f"JSON解析警告: {e}"
            )
    
    def _extract_score(self, text: str) -> float:
        """从文本中提取分数"""
        patterns = [
            r'["\']score["\']\s*:\s*(\d+)',
            r'Score[:：]\s*(\d+)',
            r'Total[:：]\s*(\d+)',
            r'(\d+)\s*points'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def get_summary(self, result: ReviewResult) -> str:
        """获取审核摘要"""
        if result.passed:
            return f"✓ 审核通过（评分：{result.score}/100）"
        else:
            issue_count = len(result.issues) if hasattr(result, 'issues') else 0
            return f"✗ 审核未通过（评分：{result.score}/100，问题：{issue_count}处）"
