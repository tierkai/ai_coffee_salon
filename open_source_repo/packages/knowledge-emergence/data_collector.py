"""
知识涌现数据采集器
负责从各种来源收集和预处理知识数据
"""

import json
import csv
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import requests
from pathlib import Path
import hashlib
import re
from dataclasses import dataclass


@dataclass
class DataSource:
    """数据源配置"""
    name: str
    type: str  # 'file', 'api', 'database', 'web'
    config: Dict[str, Any]
    enabled: bool = True


class DataCollector:
    """知识涌现数据采集器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.data_sources = self._load_data_sources()
        self.raw_data = []
        self.processed_data = []
        
    def _load_data_sources(self) -> List[DataSource]:
        """加载数据源配置"""
        default_sources = [
            DataSource(
                name="knowledge_base",
                type="file",
                config={"path": "data/knowledge_base.json"},
                enabled=True
            ),
            DataSource(
                name="research_papers",
                type="api",
                config={"url": "https://api.semanticscholar.org/graph/v1/paper/search"},
                enabled=False
            ),
            DataSource(
                name="web_content",
                type="web",
                config={"urls": [], "crawl_depth": 2},
                enabled=False
            )
        ]
        
        if 'data_sources' in self.config:
            sources = []
            for source_config in self.config['data_sources']:
                sources.append(DataSource(**source_config))
            return sources
        
        return default_sources
    
    def collect_from_file(self, file_path: str, file_type: str = 'auto') -> List[Dict[str, Any]]:
        """从文件采集数据"""
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                return []
            
            data = []
            
            if file_type == 'auto':
                file_type = path.suffix.lower()
            
            if file_type == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        data = content
                    else:
                        data = [content]
                        
            elif file_type == '.csv':
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                    
            elif file_type in ['.txt', '.md']:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单的文本分割和结构化
                    lines = content.split('\n')
                    data = [{"text": line.strip(), "source": str(path)} 
                           for line in lines if line.strip()]
            
            self.logger.info(f"从文件 {file_path} 采集到 {len(data)} 条数据")
            return data
            
        except Exception as e:
            self.logger.error(f"从文件采集数据失败: {e}")
            return []
    
    def collect_from_api(self, api_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从API采集数据"""
        try:
            url = api_config.get('url')
            headers = api_config.get('headers', {})
            params = api_config.get('params', {})
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                data = data['data']
            elif not isinstance(data, list):
                data = [data]
            
            self.logger.info(f"从API {url} 采集到 {len(data)} 条数据")
            return data
            
        except Exception as e:
            self.logger.error(f"从API采集数据失败: {e}")
            return []
    
    def collect_from_database(self, db_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从数据库采集数据"""
        try:
            db_path = db_config.get('path')
            query = db_config.get('query', 'SELECT * FROM knowledge_items')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            self.logger.info(f"从数据库 {db_path} 采集到 {len(data)} 条数据")
            return data
            
        except Exception as e:
            self.logger.error(f"从数据库采集数据失败: {e}")
            return []
    
    def collect_from_web(self, urls: List[str], max_depth: int = 1) -> List[Dict[str, Any]]:
        """从网页采集数据（简化版）"""
        data = []
        
        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # 简单的文本提取（实际应用中应使用更专业的爬虫）
                content = response.text
                
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                title = title_match.group(1) if title_match else "Unknown"
                
                # 提取正文文本
                text_content = re.sub(r'<[^>]+>', '', content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                data.append({
                    "url": url,
                    "title": title,
                    "content": text_content[:1000],  # 限制长度
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"从网页 {url} 采集数据失败: {e}")
        
        self.logger.info(f"从网页采集到 {len(data)} 条数据")
        return data
    
    def collect_data(self, source_name: str = None) -> List[Dict[str, Any]]:
        """统一的数据采集接口"""
        all_data = []
        
        sources_to_collect = (
            [source for source in self.data_sources if source.name == source_name]
            if source_name
            else [source for source in self.data_sources if source.enabled]
        )
        
        for source in sources_to_collect:
            try:
                if source.type == 'file':
                    data = self.collect_from_file(
                        source.config['path'],
                        source.config.get('file_type', 'auto')
                    )
                    
                elif source.type == 'api':
                    data = self.collect_from_api(source.config)
                    
                elif source.type == 'database':
                    data = self.collect_from_database(source.config)
                    
                elif source.type == 'web':
                    urls = source.config.get('urls', [])
                    depth = source.config.get('crawl_depth', 1)
                    data = self.collect_from_web(urls, depth)
                    
                else:
                    self.logger.warning(f"未知的数据源类型: {source.type}")
                    continue
                
                # 为数据添加元信息
                for item in data:
                    item['_source'] = source.name
                    item['_collection_time'] = datetime.now().isoformat()
                    item['_data_hash'] = hashlib.md5(
                        json.dumps(item, sort_keys=True).encode()
                    ).hexdigest()
                
                all_data.extend(data)
                
            except Exception as e:
                self.logger.error(f"采集数据源 {source.name} 失败: {e}")
        
        self.raw_data = all_data
        self.logger.info(f"总共采集到 {len(all_data)} 条数据")
        return all_data
    
    def preprocess_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """数据预处理"""
        processed = []
        
        for item in data:
            try:
                processed_item = self._clean_item(item)
                if processed_item:
                    processed.append(processed_item)
                    
            except Exception as e:
                self.logger.warning(f"预处理数据项失败: {e}")
        
        self.processed_data = processed
        self.logger.info(f"预处理完成，得到 {len(processed)} 条有效数据")
        return processed
    
    def _clean_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """清洗单个数据项"""
        if not isinstance(item, dict):
            return None
        
        # 移除空值和无效字段
        cleaned = {}
        for key, value in item.items():
            if key.startswith('_'):  # 保留元信息
                cleaned[key] = value
            elif value is not None and str(value).strip():
                # 清理文本
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    # 移除多余的空白字符
                    cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
                else:
                    cleaned_value = value
                cleaned[key] = cleaned_value
        
        # 确保有基本字段
        if not any(key in cleaned for key in ['text', 'content', 'title', 'description']):
            return None
        
        return cleaned
    
    def save_data(self, data: List[Dict[str, Any]], output_path: str, format: str = 'json'):
        """保存采集的数据"""
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'json':
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            elif format == 'csv':
                if not data:
                    return
                
                fieldnames = list(data[0].keys())
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            self.logger.info(f"数据已保存到 {output_path}")
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
    
    def get_data_stats(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        if not self.raw_data:
            return {"total": 0}
        
        stats = {
            "total": len(self.raw_data),
            "sources": {},
            "fields": set(),
            "processing_status": {
                "raw": len(self.raw_data),
                "processed": len(self.processed_data),
                "valid": len([item for item in self.processed_data if item])
            }
        }
        
        for item in self.raw_data:
            source = item.get('_source', 'unknown')
            stats["sources"][source] = stats["sources"].get(source, 0) + 1
            
            for key in item.keys():
                stats["fields"].add(key)
        
        stats["fields"] = list(stats["fields"])
        
        return stats