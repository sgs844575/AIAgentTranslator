"""
原语言分析专家 - 分析原文的语言特征、复杂度和关键信息
"""
import json
import re
from typing import Dict, Any

from .base_agent import BaseAgent
from models import AgentResult, AgentStatus, AnalysisResult, TranslationContext


class SourceAnalyzer(BaseAgent):
    """
    原语言分析专家
    
    职责：
    1. 识别原文语言类型
    2. 分析文本复杂度
    3. 提取关键术语
    4. 识别场景类型和语气风格
    5. 标注特殊元素
    """
    
    name = "原语言分析专家"
    description = "分析原文语言特征、复杂度和关键信息"
    
    def get_system_prompt(self, context: TranslationContext) -> str:
        """获取系统提示词"""
        return """你是一位语言分析专家。请分析原文，输出JSON格式报告。

## 分析维度

1. **语言识别**：源语言及变体
2. **场景类型**：文学/技术/商务/日常/游戏/敏感内容等
3. **复杂度**：简单/中等/复杂
4. **关键术语**：专业术语、专有名词、文化词汇
5. **特殊元素**：格式标签、占位符、特殊字符
6. **语气风格**：正式程度、情感基调
7. **文化注释**：需要特别注意的翻译难点

## 输出格式（JSON）

```json
{
    "language": "语言名称",
    "language_code": "语言代码",
    "scene_type": "场景类型",
    "complexity": "简单/中等/复杂",
    "complexity_reason": "复杂度理由",
    "key_terms": [
        {"term": "原文术语", "type": "类型", "translation_strategy": "翻译策略"}
    ],
    "special_elements": {
        "format_tags": ["格式标签"],
        "special_chars": ["特殊字符"],
        "placeholders": ["占位符"]
    },
    "tone_style": {
        "formality": "正式程度",
        "emotion": "情感基调"
    },
    "cultural_notes": ["文化注释"],
    "translation_strategy": "整体翻译策略"
}
```

## 注意事项
- 术语提取要全面
- 特殊字符必须完整记录
- 目标语言需流畅自然"""

    def process(self, context: TranslationContext) -> AgentResult:
        """执行分析"""
        source_text = context.source_text
        
        user_content = f"请分析以下文本：\n\n{source_text}"
        
        system_prompt = self.get_system_prompt(context)
        response = self._call_llm(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.2,
            top_p=0.1
        )
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = json.loads(response)
            
            result = AnalysisResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                output=json.dumps(analysis_data, ensure_ascii=False, indent=2),
                language=analysis_data.get('language', ''),
                complexity=analysis_data.get('complexity', ''),
                key_terms=[t.get('term', '') for t in analysis_data.get('key_terms', [])],
                tone_style=analysis_data.get('tone_style', {}).get('formality', ''),
                cultural_notes=analysis_data.get('cultural_notes', []),
                details=analysis_data
            )
            
            context.analysis_result = result
            context.source_language = analysis_data.get('language', context.source_language)
            
            return result
            
        except json.JSONDecodeError as e:
            return AnalysisResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                output=response,
                error=f"JSON parsing warning: {e}",
                language="unknown",
                complexity="unknown"
            )
