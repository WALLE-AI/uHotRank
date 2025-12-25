# 技术内容检测功能说明

## 功能概述

新增了智能检测功能，可以从爬取的文章中自动识别：
- 新开源项目
- 大模型前沿技术（LLM、GPT、Claude 等）
- RAG（检索增强生成）技术
- Agent（智能体）技术
- AI 框架和工具
- 模型训练和推理优化技术

## 核心函数

### 1. `detect_tech_content(text, title="")`

检测单篇文章是否包含技术内容。

**参数：**
- `text`: 文章正文内容
- `title`: 文章标题（可选，用于增强检测准确度）

**返回值：**
```python
{
    "is_tech_related": bool,      # 是否技术相关
    "categories": list,            # 匹配的技术分类
    "keywords": list,              # 匹配到的关键词
    "confidence": float,           # 置信度 (0-1)
    "summary": str                 # 简短说明
}
```

**使用示例：**
```python
from backend.agent.agent_today_data import detect_tech_content

result = detect_tech_content(
    text="OpenAI 发布了新版 GPT-4 模型，支持更长的上下文...",
    title="OpenAI 发布 GPT-4 Turbo"
)

if result['is_tech_related']:
    print(f"技术分类: {result['categories']}")
    print(f"置信度: {result['confidence']}")
```

### 2. `filter_tech_articles(articles)`

从文章列表中批量筛选技术相关文章。

**参数：**
- `articles`: 文章列表，每篇文章需包含 `title` 和 `content` 字段

**返回值：**
- 筛选后的技术文章列表，每篇文章会添加 `tech_detection` 字段

**使用示例：**
```python
from backend.agent.agent_today_data import filter_tech_articles

articles = [
    {"title": "...", "content": "..."},
    {"title": "...", "content": "..."}
]

tech_articles = filter_tech_articles(articles)
print(f"发现 {len(tech_articles)} 篇技术文章")
```

### 3. `scrape_and_filter_tech_articles()`

完整流程：爬取文章 → 提取内容 → 筛选技术文章。

**使用示例：**
```python
from backend.agent.agent_today_data import scrape_and_filter_tech_articles

# 一键执行完整流程
tech_articles = scrape_and_filter_tech_articles()

# 结果会自动保存到 tech_articles.jsonl
```

## 技术分类

系统会检测以下技术领域：

1. **开源项目** - 开源、GitHub、新项目发布等
2. **大模型** - GPT、Claude、LLM、语言模型等
3. **RAG技术** - 检索增强、向量数据库、Embedding 等
4. **Agent技术** - 智能体、Multi-Agent、ReAct 等
5. **AI框架** - LangChain、LlamaIndex、Transformers 等
6. **模型训练** - 微调、LoRA、RLHF、量化等
7. **推理优化** - vLLM、TensorRT、推理加速等

## 置信度计算

- 基础分：匹配的技术分类数量（每个 0.2 分，最高 0.6）
- 关键词加分：匹配的关键词数量（每个 0.05 分，最高 0.3）
- 标题加分：标题中包含关键词（每个 0.05 分，最高 0.1）
- 阈值：置信度 >= 0.2 才会被标记为技术相关

## 测试

运行测试脚本查看效果：

```bash
python test_tech_detection.py
```

## 自定义关键词

如需添加新的技术领域或关键词，编辑 `backend/agent/agent_today_data.py` 中的 `TECH_KEYWORDS` 配置：

```python
TECH_KEYWORDS = {
    "新领域名称": [
        "关键词1", "关键词2", "keyword3"
    ],
    # ... 其他分类
}
```
