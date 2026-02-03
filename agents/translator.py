"""
翻译专家 - 根据分析结果进行高质量翻译
"""
import json
import re
from typing import Dict, Any

from .base_agent import BaseAgent
from models import AgentResult, AgentStatus, TranslationResult, TranslationContext


class Translator(BaseAgent):
    """
    翻译专家
    
    职责：
    1. 根据分析结果进行专业翻译
    2. 保持格式完整
    3. 保持原文语气和风格
    4. 准确翻译关键术语
    """
    
    name = "翻译专家"
    description = "根据分析结果进行高质量翻译"
    
    def get_system_prompt(self, context: TranslationContext) -> str:
        """获取系统提示词"""
        base_prompt = """你是一位专业翻译。请将源文本翻译成目标语言。

## 翻译原则

1. **准确性**：完整传达原文意思，无遗漏、无错译
2. **格式保留**：保留所有格式标签、占位符、特殊字符
3. **术语一致**：关键术语翻译统一
4. **语气保持**：保持原文语气和风格
5. **流畅自然**：译文符合目标语言习惯，避免翻译腔

## 技术要求

- 保留编号、占位符（如 `%s`、`{var}`、`<tag>`）
- 保留全角符号（如「」『』）与原文一致
- 保留换行、空格等格式
- 不添加注释或说明

## 输出格式

<translation>
翻译内容（包含所有保留的格式标记）
</translation>"""

        # 添加分析结果
        if context.analysis_result and context.analysis_result.details:
            analysis = context.analysis_result.details
            analysis_info = f"""

## 参考信息

- 源语言：{analysis.get('language', '未知')}
- 场景：{analysis.get('scene_type', '未知')}
- 复杂度：{analysis.get('complexity', '未知')}
- 语气：{analysis.get('tone_style', {}).get('formality', '未知')}
"""
            if analysis.get('key_terms'):
                analysis_info += "\n关键术语：\n"
                for term in analysis.get('key_terms', [])[:5]:
                    analysis_info += f"- {term.get('term', '')}: {term.get('translation_strategy', '')}\n"
            
            base_prompt += analysis_info
        
        # 添加审核反馈
        if context.review_result and hasattr(context.review_result, 'issues'):
            issues = context.review_result.issues if hasattr(context.review_result, 'issues') else []
            if issues:
                review_info = "\n\n## 需改进的问题\n"
                for i, issue in enumerate(issues[:3], 1):
                    review_info += f"{i}. [{issue.get('type', '')}] {issue.get('suggestion', '')}\n"
                base_prompt += review_info
        
        return base_prompt
    
    def process(self, context: TranslationContext) -> AgentResult:
        """执行翻译"""
        source_text = context.source_text
        target_language = context.target_language
        
        user_content = f"请翻译成{target_language}：\n\n{source_text}"
        
        system_prompt = self.get_system_prompt(context)
        response = self._call_llm(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=context.temperature,
            top_p=context.top_p
        )
        
        translation = self._extract_translation(response)
        
        result = TranslationResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=translation,
            translation=translation,
            confidence=0.8,
            notes=[],
            details={}
        )
        
        context.translation_result = result
        return result
    
    def _extract_translation(self, response: str) -> str:
        """提取翻译内容"""
        pattern = re.compile(r"<translation>(.*?)</translation>", re.DOTALL)
        match = pattern.search(response)
        if match:
            return match.group(1).strip()
        
        clean_response = re.sub(r'<context_think>[\s\S]*?</context_think>', '', response).strip()
        return clean_response if clean_response else response.strip()
