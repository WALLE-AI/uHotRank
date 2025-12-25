# 文档去重检测功能

## 功能概述

系统在插入文档到 Elasticsearch 之前，会自动检测是否存在重复或相似的文档，支持三种检测方式：

1. **URL 匹配** - 检查是否存在相同 URL 的文档（精确匹配）
2. **标题匹配** - 检查是否存在相同标题的文档（精确匹配）
3. **内容相似度** - 检查是否存在内容相似的文档（模糊匹配）

## 快速使用

### 方式 1：使用默认配置（推荐）

```bash
# 默认启用去重检测，跳过重复文档
python main.py
```

### 方式 2：交互式配置

```bash
python run_crawler.py
```

会提示：
- 是否启用去重检测？
- 是否跳过重复文档？（或选择覆盖）

### 方式 3：编程方式

```python
from backend.agent.agent_today_data import scrape_all_articles_to_es

result = scrape_all_articles_to_es(
    es_index_name="tophub_articles",
    batch_size=10,
    check_duplicate=True,   # 启用去重检测
    skip_duplicate=True     # 跳过重复文档
)

print(f"成功: {result['success']}")
print(f"失败: {result['failed']}")
print(f"重复: {result['duplicate']}")
```

## 检测方式详解

### 1. URL 匹配（默认启用）

检查 `original_url` 或 `tophub_url` 是否已存在。

```python
from backend.db import ElasticsearchClient, ArticleRepository

es_client = ElasticsearchClient()
repo = ArticleRepository(es_client)

# 查找重复 URL
duplicate = repo.find_duplicate_by_url("https://example.com/article")

if duplicate:
    print(f"找到重复文档: {duplicate['title']}")
```

**特点：**
- 最快速、最准确
- 适合防止完全相同的文章重复
- 推荐始终启用

### 2. 标题匹配（默认启用）

检查是否存在完全相同的标题。

```python
# 查找重复标题
duplicate = repo.find_duplicate_by_title("GPT-4 发布")

if duplicate:
    print(f"找到重复标题: {duplicate['title']}")
```

**特点：**
- 精确匹配标题
- 适合防止标题相同但 URL 不同的重复
- 推荐启用

### 3. 内容相似度检测（可选）

使用 Elasticsearch 的 More Like This 查询，检测内容相似的文档。

```python
# 查找相似文档
similar_docs = repo.find_similar_documents(
    title="GPT-4 的新功能",
    content="OpenAI 发布了 GPT-4...",
    min_score=0.7,  # 最小相似度
    size=5
)

for doc in similar_docs:
    print(f"{doc['title']} - 相似度: {doc['_score']:.2f}")
```

**特点：**
- 可以检测内容相似但标题/URL 不同的文章
- 计算开销较大
- 适合需要严格去重的场景

### 4. 综合检测

```python
# 综合检测（推荐配置）
result = repo.check_duplicate(
    document=article,
    check_url=True,          # 检查 URL
    check_title=True,        # 检查标题
    check_similarity=False,  # 不检查相似度（可选）
    similarity_threshold=0.7 # 相似度阈值
)

if result['is_duplicate']:
    print(f"发现重复: {result['duplicate_type']}")
    print(f"相似度: {result['similarity_score']}")
    print(f"重复文档: {result['duplicate_doc']['title']}")
```

## API 参考

### ArticleRepository.check_duplicate()

综合检查文档是否重复。

```python
result = repo.check_duplicate(
    document: Dict[str, Any],           # 待检查的文档
    check_url: bool = True,             # 是否检查 URL
    check_title: bool = True,           # 是否检查标题
    check_similarity: bool = False,     # 是否检查相似度
    similarity_threshold: float = 0.7   # 相似度阈值
)
```

**返回值：**
```python
{
    "is_duplicate": bool,      # 是否重复
    "duplicate_type": str,     # 重复类型: "url", "title", "similar", None
    "duplicate_doc": dict,     # 重复的文档（如果存在）
    "similarity_score": float  # 相似度分数
}
```

### ArticleRepository.find_duplicate_by_url()

通过 URL 查找重复文档。

```python
duplicate = repo.find_duplicate_by_url(url: str)
```

### ArticleRepository.find_duplicate_by_title()

通过标题查找重复文档。

```python
duplicate = repo.find_duplicate_by_title(
    title: str,
    threshold: float = 0.9
)
```

### ArticleRepository.find_similar_documents()

查找相似文档。

```python
similar_docs = repo.find_similar_documents(
    title: str,
    content: str,
    min_score: float = 0.7,
    size: int = 5
)
```

### ArticleRepository.document_exists()

检查文档 ID 是否存在。

```python
exists = repo.document_exists(doc_id: str)
```

## 使用场景

### 场景 1：首次爬取（不检查重复）

```python
result = scrape_all_articles_to_es(
    check_duplicate=False  # 禁用去重
)
```

### 场景 2：增量更新（跳过重复）

```python
result = scrape_all_articles_to_es(
    check_duplicate=True,   # 启用去重
    skip_duplicate=True     # 跳过重复
)
```

### 场景 3：强制更新（覆盖重复）

```python
result = scrape_all_articles_to_es(
    check_duplicate=True,   # 启用去重
    skip_duplicate=False    # 覆盖重复
)
```

### 场景 4：严格去重（包含相似度检测）

修改 `agent_today_data.py` 中的检测配置：

```python
dup_result = repo.check_duplicate(
    article_content,
    check_url=True,
    check_title=True,
    check_similarity=True,      # 启用相似度检测
    similarity_threshold=0.7    # 相似度阈值
)
```

## 性能考虑

### 检测速度

1. **URL 匹配**: 最快（直接通过 ID 查询）
2. **标题匹配**: 快速（精确匹配查询）
3. **相似度检测**: 较慢（需要分析文本）

### 推荐配置

**日常使用（平衡模式）：**
```python
check_url=True,
check_title=True,
check_similarity=False  # 不启用相似度检测
```

**严格去重（高质量模式）：**
```python
check_url=True,
check_title=True,
check_similarity=True,
similarity_threshold=0.7
```

**快速模式（仅 URL）：**
```python
check_url=True,
check_title=False,
check_similarity=False
```

## 测试

运行测试脚本：

```bash
python test_duplicate_detection.py
```

测试内容：
- URL 重复检测
- 标题重复检测
- 内容相似度检测
- 完全不同文档的检测
- 查找相似文档

## 常见问题

### Q1: 为什么有些重复文档没有被检测到？

**可能原因：**
1. URL 或标题略有不同
2. 相似度检测未启用或阈值太高
3. 文档内容差异较大

**解决方案：**
- 启用相似度检测
- 降低相似度阈值（如 0.5）

### Q2: 相似度检测太慢怎么办？

**解决方案：**
1. 只在必要时启用相似度检测
2. 减少检测的内容长度（默认只用前 1000 字符）
3. 提高相似度阈值（减少匹配数量）

### Q3: 如何查看被跳过的重复文档？

查看日志输出，会显示：
```
⏭️  跳过重复文档 (类型: url)
```

### Q4: 如何强制覆盖所有文档？

```python
scrape_all_articles_to_es(
    check_duplicate=False  # 禁用去重检测
)
```

或

```python
scrape_all_articles_to_es(
    check_duplicate=True,
    skip_duplicate=False  # 覆盖重复文档
)
```

### Q5: 相似度分数如何理解？

- **1.0**: 完全相同（URL 或标题精确匹配）
- **0.7-0.9**: 高度相似（内容大部分相同）
- **0.5-0.7**: 中等相似（部分内容相同）
- **< 0.5**: 低相似度（基本不同）

## 最佳实践

1. **首次爬取**: 禁用去重检测，快速导入所有数据
2. **增量更新**: 启用去重检测，跳过重复文档
3. **定期清理**: 使用相似度检测找出重复文档并清理
4. **监控日志**: 关注重复文档的数量和类型

## 下一步

- 查看 [USAGE.md](USAGE.md) 了解更多使用方法
- 查看 [ELASTICSEARCH_GUIDE.md](ELASTICSEARCH_GUIDE.md) 了解 ES API
- 运行 `test_duplicate_detection.py` 测试功能
