# AI Agent Translator

基于多Agent协作的智能翻译工具，采用四位专家协同工作架构，实现高质量的机器翻译。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特点

- **多Agent协作**：四位专家Agent协同工作，层层把关翻译质量
- **智能分析**：自动分析原文语言特征、复杂度和关键术语
- **质量审核**：多维度审核评分，确保翻译准确性
- **迭代优化**：支持自动迭代优化，直至达到质量标准
- **可视化界面**：直观展示工作流程和各Agent状态
- **灵活配置**：支持自定义模型、参数和审核阈值

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Agent Translator                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                        │
│  │  原语言分析专家  │ ← 分析原文语言特征、复杂度、关键术语    │
│  │ SourceAnalyzer  │                                        │
│  └────────┬────────┘                                        │
│           ↓                                                 │
│  ┌─────────────────┐                                        │
│  │   翻译专家       │ ← 根据分析结果进行高质量翻译           │
│  │   Translator    │                                        │
│  └────────┬────────┘                                        │
│           ↓                                                 │
│  ┌─────────────────┐     ┌──────────────┐                  │
│  │  翻译审核专家    │ ←→ │  未通过反馈   │                  │
│  │   Reviewer      │     └──────────────┘                  │
│  └────────┬────────┘              ↑                        │
│           ↓ (通过)                │                        │
│  ┌─────────────────┐              │                        │
│  │  翻译优化专家    │ ←────────────┘                        │
│  │   Optimizer     │   优化后重新翻译                      │
│  └────────┬────────┘                                        │
│           ↓                                                 │
│  ┌─────────────────┐                                        │
│  │    最终译文      │                                        │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- PyQt5 5.15+
- OpenAI API 或其他兼容 API

### 安装依赖

```bash
pip install PyQt5 requests
```

### 配置 API

编辑 `config/TranslateConfig.json`：

```json
{
  "model_config": {
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4",
    "api_key_list": ["your-api-key-here"]
  }
}
```

### 启动应用

```bash
python run.py
```

或

```bash
python Main.py
```

## 📖 使用说明

### 基本流程

1. **输入原文**：在左侧文本框输入待翻译内容
2. **选择目标语言**：从下拉菜单选择目标语言
3. **设置参数**：调整创意程度（Temperature）和多样性（Top-p）
4. **开始翻译**：点击"开始翻译"按钮
5. **查看结果**：右侧显示最终译文，左侧面板显示各Agent工作状态

### 工作流模式

- **标准模式**：分析 → 翻译 → 审核 → 优化 → 输出
- **迭代模式**：审核未通过时自动重新翻译优化（最多3轮）

### 审核评分标准

| 维度 | 权重 | 说明 |
|------|------|------|
| 准确性 | 35% | 意思完整、语气准确 |
| 技术规范 | 25% | 格式标签、占位符完整 |
| 术语一致性 | 20% | 术语统一 |
| 语言表达 | 15% | 流畅自然 |
| 格式规范 | 5% | 标点、空格正确 |

**评分等级**：
- 90-100分：优秀
- 80-89分：良好（通过）
- 70-79分：一般（需修改）
- <70分：不合格

## ⚙️ 配置说明

### 模型配置 (`config/TranslateConfig.json`)

```json
{
  "model_config": {
    "base_url": "API基础地址",
    "model": "模型名称",
    "api_key_list": ["API密钥列表"]
  }
}
```

支持 OpenAI、SiliconFlow 等兼容 OpenAI API 格式的服务。

### Agent配置 (`config/agents_config.json`)

```json
{
  "agents": {
    "reviewer": {
      "pass_threshold": 80,
      "weights": {
        "accuracy": 35,
        "technical": 25,
        "terminology": 20,
        "language": 15,
        "format": 5
      }
    }
  },
  "workflow": {
    "enable_iteration": true,
    "max_iterations": 3
  }
}
```

## 📁 项目结构

```
TranslateToolsUi/
├── agents/                     # Agent专家模块
│   ├── base_agent.py          # 基础Agent类
│   ├── source_analyzer.py     # 原语言分析专家
│   ├── translator.py          # 翻译专家
│   ├── reviewer.py            # 翻译审核专家
│   └── optimizer.py           # 翻译优化专家
├── core/                       # 核心模块
│   ├── agent_orchestrator.py  # Agent协调器
│   └── translation_pipeline.py # 翻译流程管理
├── gui/                        # GUI界面模块
│   ├── main_window.py         # 主窗口
│   ├── agent_panel.py         # Agent状态面板
│   └── workflow_visualizer.py # 工作流可视化
├── models/                     # 数据模型
│   ├── agent_result.py        # Agent结果模型
│   └── translation_context.py # 翻译上下文
├── clinet/                     # LLM客户端
│   └── LLMClient.py
├── config/                     # 配置文件
│   ├── TranslateConfig.json   # 翻译配置
│   └── agents_config.json     # Agent配置
├── Main.py                     # 入口文件
├── run.py                      # 启动脚本
└── README.md                   # 项目说明
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证开源。

```
MIT License

Copyright (c) 2024 AI Agent Translator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 致谢

- [OpenAI](https://openai.com/) - 提供大语言模型 API
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
- [SiliconFlow](https://siliconflow.cn/) - 国内模型 API 服务

---

<p align="center">Made with ❤️ by AI Agent Translator Team</p>
