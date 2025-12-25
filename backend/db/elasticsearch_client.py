"""
Elasticsearch 客户端封装
支持 Elasticsearch 9.2.1
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Elasticsearch 客户端封装类"""
    
    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_certs: bool = True,
        ca_certs: Optional[str] = None
    ):
        """
        初始化 Elasticsearch 客户端
        
        Args:
            hosts: ES 主机地址列表，默认从环境变量读取
            api_key: API Key 认证
            username: 用户名（基础认证）
            password: 密码（基础认证）
            verify_certs: 是否验证 SSL 证书
            ca_certs: CA 证书路径
        """
        # 从环境变量读取配置
        if hosts is None:
            es_host = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
            hosts = [es_host]
        
        if api_key is None:
            api_key = os.getenv("ELASTICSEARCH_API_KEY")
        
        if username is None:
            username = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
        
        if password is None:
            password = os.getenv("ELASTICSEARCH_PASSWORD")
        
        # 构建连接参数
        connection_params = {
            "hosts": hosts,
            "verify_certs": verify_certs,
        }
        
        # 认证方式：优先使用 API Key
        if api_key:
            connection_params["api_key"] = api_key
        elif username and password:
            connection_params["basic_auth"] = (username, password)
        
        if ca_certs:
            connection_params["ca_certs"] = ca_certs
        
        try:
            self.client = Elasticsearch(**connection_params)
            # 测试连接
            info = self.client.info()
            logger.info(f"✅ 成功连接到 Elasticsearch {info['version']['number']}")
        except Exception as e:
            logger.error(f"❌ 连接 Elasticsearch 失败: {e}")
            raise
    
    def ping(self) -> bool:
        """测试连接是否正常"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Ping 失败: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Elasticsearch 集群信息"""
        return self.client.info()
    
    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info("Elasticsearch 连接已关闭")


class ArticleRepository:
    """文章数据仓库 - 封装 CRUD 操作"""
    
    def __init__(self, es_client: ElasticsearchClient, index_name: str = "tophub_articles"):
        """
        初始化文章仓库
        
        Args:
            es_client: Elasticsearch 客户端实例
            index_name: 索引名称
        """
        self.es = es_client.client
        self.index_name = index_name
    
    def create_index(self, delete_if_exists: bool = False) -> bool:
        """
        创建索引
        
        Args:
            delete_if_exists: 如果索引已存在是否删除
        
        Returns:
            bool: 是否创建成功
        """
        try:
            # 检查索引是否存在
            if self.es.indices.exists(index=self.index_name):
                if delete_if_exists:
                    logger.warning(f"索引 {self.index_name} 已存在，正在删除...")
                    self.es.indices.delete(index=self.index_name)
                else:
                    logger.info(f"索引 {self.index_name} 已存在")
                    return True
            
            # 定义索引映射
            mappings = {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "category": {
                        "type": "keyword"
                    },
                    "original_url": {
                        "type": "keyword"
                    },
                    "tophub_url": {
                        "type": "keyword"
                    },
                    "publish_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart"
                    },
                    "images": {
                        "type": "keyword"
                    },
                    "scraped_at": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                    },
                    "tech_detection": {
                        "properties": {
                            "is_tech_related": {"type": "boolean"},
                            "categories": {"type": "keyword"},
                            "keywords": {"type": "keyword"},
                            "confidence": {"type": "float"},
                            "summary": {"type": "text"}
                        }
                    },
                    "content_analysis": {
                        "properties": {
                            "keywords": {"type": "keyword"},
                            "topics": {"type": "keyword"},
                            "summary": {
                                "type": "text",
                                "analyzer": "ik_max_word",
                                "search_analyzer": "ik_smart"
                            },
                            "sentiment": {"type": "keyword"},
                            "category": {"type": "keyword"},
                            "entities": {
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "type": {"type": "keyword"}
                                }
                            },
                            "analysis_success": {"type": "boolean"}
                        }
                    },
                    "status": {
                        "type": "keyword"
                    },
                    "error": {
                        "type": "text"
                    }
                }
            }
            
            # 创建索引
            self.es.indices.create(
                index=self.index_name,
                mappings=mappings,
                settings={
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                }
            )
            
            logger.info(f"✅ 索引 {self.index_name} 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建索引失败: {e}")
            return False
    
    def index_exists(self) -> bool:
        """检查索引是否存在"""
        return self.es.indices.exists(index=self.index_name)
    
    def create_document(self, document: Dict[str, Any], doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        创建单个文档
        
        Args:
            document: 文档数据
            doc_id: 文档 ID（可选，不指定则自动生成）
        
        Returns:
            创建结果
        """
        try:
            result = self.es.index(
                index=self.index_name,
                id=doc_id,
                document=document
            )
            logger.info(f"✅ 文档创建成功: {result['_id']}")
            return result
        except Exception as e:
            logger.error(f"❌ 创建文档失败: {e}")
            raise
    
    def bulk_create_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量创建文档
        
        Args:
            documents: 文档列表
        
        Returns:
            批量操作结果统计
        """
        try:
            # 准备批量操作数据
            actions = []
            for doc in documents:
                action = {
                    "_index": self.index_name,
                    "_source": doc
                }
                # 如果文档有 URL，使用 URL 作为 ID（避免重复）
                if "original_url" in doc:
                    action["_id"] = doc["original_url"]
                elif "tophub_url" in doc:
                    action["_id"] = doc["tophub_url"]
                
                actions.append(action)
            
            # 执行批量操作
            success, failed = bulk(self.es, actions, raise_on_error=False)
            
            logger.info(f"✅ 批量创建完成: 成功 {success} 条, 失败 {len(failed)} 条")
            
            return {
                "success": success,
                "failed": len(failed),
                "failed_items": failed
            }
            
        except Exception as e:
            logger.error(f"❌ 批量创建失败: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个文档
        
        Args:
            doc_id: 文档 ID
        
        Returns:
            文档数据，不存在返回 None
        """
        try:
            result = self.es.get(index=self.index_name, id=doc_id)
            return result["_source"]
        except Exception as e:
            logger.warning(f"获取文档失败: {e}")
            return None
    
    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新文档
        
        Args:
            doc_id: 文档 ID
            updates: 要更新的字段
        
        Returns:
            更新结果
        """
        try:
            result = self.es.update(
                index=self.index_name,
                id=doc_id,
                doc=updates
            )
            logger.info(f"✅ 文档更新成功: {doc_id}")
            return result
        except Exception as e:
            logger.error(f"❌ 更新文档失败: {e}")
            raise
    
    def document_exists(self, doc_id: str) -> bool:
        """
        检查文档是否存在
        
        Args:
            doc_id: 文档 ID
        
        Returns:
            bool: 文档是否存在
        """
        try:
            return self.es.exists(index=self.index_name, id=doc_id)
        except Exception as e:
            logger.error(f"检查文档存在性失败: {e}")
            return False
    
    def find_duplicate_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通过 URL 查找重复文档
        
        Args:
            url: 文章 URL
        
        Returns:
            重复的文档，不存在返回 None
        """
        try:
            # 尝试通过 URL 作为 ID 查找
            if self.document_exists(url):
                return self.get_document(url)
            
            # 通过查询查找
            query = {
                "bool": {
                    "should": [
                        {"term": {"original_url.keyword": url}},
                        {"term": {"tophub_url.keyword": url}}
                    ],
                    "minimum_should_match": 1
                }
            }
            
            result = self.search(query=query, size=1)
            hits = result.get("hits", {}).get("hits", [])
            
            if hits:
                doc = hits[0]["_source"]
                doc["_id"] = hits[0]["_id"]
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"查找重复 URL 失败: {e}")
            return None
    
    def find_duplicate_by_title(self, title: str, threshold: float = 0.9) -> Optional[Dict[str, Any]]:
        """
        通过标题查找重复文档（精确匹配）
        
        Args:
            title: 文章标题
            threshold: 相似度阈值（0-1）
        
        Returns:
            重复的文档，不存在返回 None
        """
        try:
            # 精确匹配
            query = {
                "match": {
                    "title.keyword": title
                }
            }
            
            result = self.search(query=query, size=1)
            hits = result.get("hits", {}).get("hits", [])
            
            if hits and hits[0]["_score"] >= threshold:
                doc = hits[0]["_source"]
                doc["_id"] = hits[0]["_id"]
                doc["_score"] = hits[0]["_score"]
                return doc
            
            return None
            
        except Exception as e:
            logger.error(f"查找重复标题失败: {e}")
            return None
    
    def find_similar_documents(
        self,
        title: str,
        content: str,
        min_score: float = 0.7,
        size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        查找相似文档（基于标题和内容）
        
        Args:
            title: 文章标题
            content: 文章内容
            min_score: 最小相似度分数
            size: 返回结果数量
        
        Returns:
            相似文档列表
        """
        try:
            # 使用 More Like This 查询
            query = {
                "more_like_this": {
                    "fields": ["title^3", "content"],  # 标题权重更高
                    "like": [
                        {
                            "doc": {
                                "title": title,
                                "content": content[:1000]  # 只使用前1000字符
                            }
                        }
                    ],
                    "min_term_freq": 1,
                    "min_doc_freq": 1,
                    "max_query_terms": 25,
                    "minimum_should_match": "30%"
                }
            }
            
            result = self.search(query=query, size=size)
            hits = result.get("hits", {}).get("hits", [])
            
            # 过滤低分文档
            similar_docs = []
            for hit in hits:
                if hit["_score"] >= min_score:
                    doc = hit["_source"]
                    doc["_id"] = hit["_id"]
                    doc["_score"] = hit["_score"]
                    similar_docs.append(doc)
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"查找相似文档失败: {e}")
            return []
    
    def check_duplicate(
        self,
        document: Dict[str, Any],
        check_url: bool = True,
        check_title: bool = True,
        check_similarity: bool = False,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        综合检查文档是否重复
        
        Args:
            document: 待检查的文档
            check_url: 是否检查 URL
            check_title: 是否检查标题
            check_similarity: 是否检查内容相似度
            similarity_threshold: 相似度阈值
        
        Returns:
            dict: {
                "is_duplicate": bool,  # 是否重复
                "duplicate_type": str,  # 重复类型: "url", "title", "similar", None
                "duplicate_doc": dict,  # 重复的文档（如果存在）
                "similarity_score": float  # 相似度分数（如果适用）
            }
        """
        result = {
            "is_duplicate": False,
            "duplicate_type": None,
            "duplicate_doc": None,
            "similarity_score": 0.0
        }
        
        # 1. 检查 URL
        if check_url:
            url = document.get("original_url") or document.get("tophub_url")
            if url:
                duplicate = self.find_duplicate_by_url(url)
                if duplicate:
                    result["is_duplicate"] = True
                    result["duplicate_type"] = "url"
                    result["duplicate_doc"] = duplicate
                    result["similarity_score"] = 1.0
                    return result
        
        # 2. 检查标题
        if check_title:
            title = document.get("title")
            if title:
                duplicate = self.find_duplicate_by_title(title)
                if duplicate:
                    result["is_duplicate"] = True
                    result["duplicate_type"] = "title"
                    result["duplicate_doc"] = duplicate
                    result["similarity_score"] = duplicate.get("_score", 1.0)
                    return result
        
        # 3. 检查内容相似度
        if check_similarity:
            title = document.get("title", "")
            content = document.get("content", "")
            
            if title or content:
                similar_docs = self.find_similar_documents(
                    title=title,
                    content=content,
                    min_score=similarity_threshold,
                    size=1
                )
                
                if similar_docs:
                    result["is_duplicate"] = True
                    result["duplicate_type"] = "similar"
                    result["duplicate_doc"] = similar_docs[0]
                    result["similarity_score"] = similar_docs[0].get("_score", 0.0)
                    return result
        
        return result
        """
        删除文档
        
        Args:
            doc_id: 文档 ID
        
        Returns:
            删除结果
        """
        try:
            result = self.es.delete(index=self.index_name, id=doc_id)
            logger.info(f"✅ 文档删除成功: {doc_id}")
            return result
        except Exception as e:
            logger.error(f"❌ 删除文档失败: {e}")
            raise
    
    def search(
        self,
        query: Optional[Dict[str, Any]] = None,
        size: int = 10,
        from_: int = 0,
        sort: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        搜索文档
        
        Args:
            query: 查询条件（ES DSL）
            size: 返回结果数量
            from_: 起始位置
            sort: 排序规则
        
        Returns:
            搜索结果
        """
        try:
            body = {}
            if query:
                body["query"] = query
            else:
                body["query"] = {"match_all": {}}
            
            if sort:
                body["sort"] = sort
            
            result = self.es.search(
                index=self.index_name,
                body=body,
                size=size,
                from_=from_
            )
            
            return result
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            raise
    
    def search_by_keyword(
        self,
        keyword: str,
        fields: Optional[List[str]] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        关键词搜索
        
        Args:
            keyword: 搜索关键词
            fields: 搜索字段列表，默认搜索 title 和 content
            size: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        if fields is None:
            fields = ["title^2", "content"]  # title 权重更高
        
        query = {
            "multi_match": {
                "query": keyword,
                "fields": fields,
                "type": "best_fields"
            }
        }
        
        result = self.search(query=query, size=size)
        
        # 提取文档
        hits = result.get("hits", {}).get("hits", [])
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]
            doc["_score"] = hit["_score"]
            documents.append(doc)
        
        return documents
    
    def search_tech_articles(
        self,
        categories: Optional[List[str]] = None,
        min_confidence: float = 0.5,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索技术相关文章
        
        Args:
            categories: 技术分类列表（可选）
            min_confidence: 最小置信度
            size: 返回结果数量
        
        Returns:
            技术文章列表
        """
        # 构建查询条件
        must_conditions = [
            {"term": {"tech_detection.is_tech_related": True}},
            {"range": {"tech_detection.confidence": {"gte": min_confidence}}}
        ]
        
        if categories:
            must_conditions.append({
                "terms": {"tech_detection.categories": categories}
            })
        
        query = {
            "bool": {
                "must": must_conditions
            }
        }
        
        # 按置信度排序
        sort = [{"tech_detection.confidence": {"order": "desc"}}]
        
        result = self.search(query=query, size=size, sort=sort)
        
        # 提取文档
        hits = result.get("hits", {}).get("hits", [])
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]
            documents.append(doc)
        
        return documents
    
    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        统计文档数量
        
        Args:
            query: 查询条件（可选）
        
        Returns:
            文档数量
        """
        try:
            if query:
                result = self.es.count(index=self.index_name, query=query)
            else:
                result = self.es.count(index=self.index_name)
            
            return result["count"]
        except Exception as e:
            logger.error(f"❌ 统计失败: {e}")
            return 0
    
    def delete_index(self) -> bool:
        """删除索引"""
        try:
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                logger.info(f"✅ 索引 {self.index_name} 已删除")
                return True
            else:
                logger.warning(f"索引 {self.index_name} 不存在")
                return False
        except Exception as e:
            logger.error(f"❌ 删除索引失败: {e}")
            return False
    
    def search_by_keywords(
        self,
        keywords: List[str],
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        通过内容分析的关键词搜索
        
        Args:
            keywords: 关键词列表
            size: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        query = {
            "terms": {
                "content_analysis.keywords": keywords
            }
        }
        
        result = self.search(query=query, size=size)
        
        hits = result.get("hits", {}).get("hits", [])
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]
            doc["_score"] = hit["_score"]
            documents.append(doc)
        
        return documents
    
    def search_by_topic(
        self,
        topic: str,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        通过主题搜索
        
        Args:
            topic: 主题
            size: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        query = {
            "term": {
                "content_analysis.topics": topic
            }
        }
        
        result = self.search(query=query, size=size)
        
        hits = result.get("hits", {}).get("hits", [])
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]
            documents.append(doc)
        
        return documents
    
    def search_by_category(
        self,
        category: str,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        通过分类搜索
        
        Args:
            category: 分类
            size: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        query = {
            "term": {
                "content_analysis.category": category
            }
        }
        
        result = self.search(query=query, size=size)
        
        hits = result.get("hits", {}).get("hits", [])
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]
            documents.append(doc)
        
        return documents
    
    def search_by_sentiment(
        self,
        sentiment: str,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        通过情感倾向搜索
        
        Args:
            sentiment: 情感倾向 (positive/neutral/negative)
            size: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        query = {
            "term": {
                "content_analysis.sentiment": sentiment
            }
        }
        
        result = self.search(query=query, size=size)
        
        hits = result.get("hits", {}).get("hits", [])
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]
            documents.append(doc)
        
        return documents
    
    def get_keyword_statistics(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        获取关键词统计
        
        Args:
            top_n: 返回前 N 个关键词
        
        Returns:
            关键词统计列表
        """
        try:
            agg_query = {
                "size": 0,
                "aggs": {
                    "keywords": {
                        "terms": {
                            "field": "content_analysis.keywords",
                            "size": top_n
                        }
                    }
                }
            }
            
            result = self.es.search(index=self.index_name, body=agg_query)
            buckets = result.get("aggregations", {}).get("keywords", {}).get("buckets", [])
            
            return [
                {"keyword": b["key"], "count": b["doc_count"]}
                for b in buckets
            ]
        except Exception as e:
            logger.error(f"获取关键词统计失败: {e}")
            return []
    
    def get_topic_statistics(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取主题统计
        
        Args:
            top_n: 返回前 N 个主题
        
        Returns:
            主题统计列表
        """
        try:
            agg_query = {
                "size": 0,
                "aggs": {
                    "topics": {
                        "terms": {
                            "field": "content_analysis.topics",
                            "size": top_n
                        }
                    }
                }
            }
            
            result = self.es.search(index=self.index_name, body=agg_query)
            buckets = result.get("aggregations", {}).get("topics", {}).get("buckets", [])
            
            return [
                {"topic": b["key"], "count": b["doc_count"]}
                for b in buckets
            ]
        except Exception as e:
            logger.error(f"获取主题统计失败: {e}")
            return []
    
    def get_category_statistics(self) -> Dict[str, int]:
        """
        获取分类统计
        
        Returns:
            分类统计字典
        """
        try:
            agg_query = {
                "size": 0,
                "aggs": {
                    "categories": {
                        "terms": {
                            "field": "content_analysis.category",
                            "size": 50
                        }
                    }
                }
            }
            
            result = self.es.search(index=self.index_name, body=agg_query)
            buckets = result.get("aggregations", {}).get("categories", {}).get("buckets", [])
            
            return {b["key"]: b["doc_count"] for b in buckets}
        except Exception as e:
            logger.error(f"获取分类统计失败: {e}")
            return {}
    
    def get_sentiment_statistics(self) -> Dict[str, int]:
        """
        获取情感统计
        
        Returns:
            情感统计字典
        """
        try:
            agg_query = {
                "size": 0,
                "aggs": {
                    "sentiments": {
                        "terms": {
                            "field": "content_analysis.sentiment"
                        }
                    }
                }
            }
            
            result = self.es.search(index=self.index_name, body=agg_query)
            buckets = result.get("aggregations", {}).get("sentiments", {}).get("buckets", [])
            
            return {b["key"]: b["doc_count"] for b in buckets}
        except Exception as e:
            logger.error(f"获取情感统计失败: {e}")
            return {}
