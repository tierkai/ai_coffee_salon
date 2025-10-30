"""
Coze API客户端
负责与Coze平台的API交互，包括认证、对话管理等
"""
import requests
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta

from .config_manager import get_config
from .auth_manager import get_auth_manager, AuthToken

logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class StreamMode(Enum):
    """流式模式"""
    STREAM = True
    NO_STREAM = False


@dataclass
class Message:
    """消息对象"""
    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    message_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """对话对象"""
    conversation_id: str
    bot_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "active"


@dataclass
class ChatRequest:
    """聊天请求"""
    bot_id: str
    query: str
    conversation_id: Optional[str] = None
    stream: bool = False
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


@dataclass
class ChatResponse:
    """聊天响应"""
    conversation_id: str
    message_id: str
    content: str
    role: MessageRole
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage: Optional[Dict[str, Any]] = None


class CozeAPIClient:
    """Coze API客户端"""
    
    def __init__(self):
        self.config = get_config()
        self.coze_config = self.config.coze
        self.auth_manager = get_auth_manager()
        self._session = requests.Session()
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        # 设置默认请求头
        self._session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Coze-Integration-SDK/1.0.0'
        })
        
        # 速率限制控制
        self._rate_limit_bucket = self.coze_config.rate_limit
        self._last_request_time = 0
    
    def _check_rate_limit(self):
        """检查速率限制"""
        current_time = time.time()
        time_diff = current_time - self._last_request_time
        
        # 重置速率限制桶（按小时）
        if time_diff >= 3600:
            self._rate_limit_bucket = self.coze_config.rate_limit
            self._last_request_time = current_time
        
        if self._rate_limit_bucket <= 0:
            wait_time = 3600 - time_diff
            logger.warning(f"达到速率限制，等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)
            self._rate_limit_bucket = self.coze_config.rate_limit
            self._last_request_time = time.time()
        
        self._rate_limit_bucket -= 1
    
    def _get_access_token(self) -> str:
        """获取访问令牌"""
        current_time = time.time()
        
        # 检查令牌是否过期
        if self._access_token and current_time < self._token_expires_at:
            return self._access_token
        
        logger.info("获取新的访问令牌")
        
        # 创建JWT令牌
        jwt_token = self.auth_manager.create_jwt_token(
            user_id="system",
            tenant_id="default",
            scope=["coze_api"]
        )
        
        # 交换访问令牌
        auth_token = self.auth_manager.exchange_access_token(jwt_token)
        self._access_token = auth_token.access_token
        self._token_expires_at = auth_token.expires_at
        
        return self._access_token
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Dict[str, Any]:
        """发起HTTP请求"""
        self._check_rate_limit()
        
        url = f"{self.coze_config.base_url}/{self.coze_config.api_version}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}'
        }
        
        try:
            if method.upper() == 'GET':
                response = self._session.get(url, headers=headers, params=params, 
                                           timeout=self.coze_config.timeout)
            elif method.upper() == 'POST':
                response = self._session.post(url, headers=headers, json=data,
                                            timeout=self.coze_config.timeout)
            elif method.upper() == 'PUT':
                response = self._session.put(url, headers=headers, json=data,
                                           timeout=self.coze_config.timeout)
            elif method.upper() == 'DELETE':
                response = self._session.delete(url, headers=headers,
                                              timeout=self.coze_config.timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                error_data = e.response.json()
                raise CozeAPIError(
                    error_data.get('message', 'Unknown error'),
                    error_data.get('code', e.response.status_code)
                )
            raise CozeAPIError(str(e))
    
    def create_conversation(self, bot_id: str) -> Conversation:
        """创建对话"""
        data = {'bot_id': bot_id}
        result = self._make_request('POST', 'conversation/create', data)
        
        conversation = Conversation(
            conversation_id=result['conversation_id'],
            bot_id=bot_id
        )
        
        logger.info(f"创建对话: {conversation.conversation_id}")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Conversation:
        """获取对话信息"""
        result = self._make_request('GET', f'conversation/{conversation_id}')
        
        messages = []
        for msg_data in result.get('messages', []):
            message = Message(
                role=MessageRole(msg_data['role']),
                content=msg_data['content'],
                timestamp=msg_data.get('timestamp', time.time()),
                message_id=msg_data.get('message_id')
            )
            messages.append(message)
        
        conversation = Conversation(
            conversation_id=result['conversation_id'],
            bot_id=result['bot_id'],
            messages=messages,
            created_at=result.get('created_at', time.time()),
            updated_at=result.get('updated_at', time.time()),
            status=result.get('status', 'active')
        )
        
        return conversation
    
    def chat(self, request: ChatRequest) -> ChatResponse:
        """发送聊天消息（非流式）"""
        data = {
            'bot_id': request.bot_id,
            'query': request.query,
            'stream': request.stream
        }
        
        if request.conversation_id:
            data['conversation_id'] = request.conversation_id
        
        if request.context:
            data['context'] = request.context
        
        result = self._make_request('POST', 'chat', data)
        
        response = ChatResponse(
            conversation_id=result['conversation_id'],
            message_id=result['message_id'],
            content=result['content'],
            role=MessageRole.ASSISTANT,
            timestamp=result.get('timestamp', time.time()),
            metadata=result.get('metadata', {}),
            usage=result.get('usage')
        )
        
        logger.info(f"发送聊天消息，响应ID: {response.message_id}")
        return response
    
    def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """发送聊天消息（流式）"""
        data = {
            'bot_id': request.bot_id,
            'query': request.query,
            'stream': True
        }
        
        if request.conversation_id:
            data['conversation_id'] = request.conversation_id
        
        if request.context:
            data['context'] = request.context
        
        url = f"{self.coze_config.base_url}/{self.coze_config.api_version}/chat"
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        try:
            with self._session.post(url, headers=headers, json=data, 
                                  stream=True, timeout=self.coze_config.timeout) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]  # 移除 'data: ' 前缀
                            if data_str.strip() == '[DONE]':
                                break
                            
                            try:
                                chunk_data = json.loads(data_str)
                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                    choice = chunk_data['choices'][0]
                                    delta = choice.get('delta', {})
                                    
                                    if 'content' in delta:
                                        response = ChatResponse(
                                            conversation_id=chunk_data.get('conversation_id', ''),
                                            message_id=chunk_data.get('message_id', ''),
                                            content=delta['content'],
                                            role=MessageRole.ASSISTANT,
                                            timestamp=time.time(),
                                            metadata=chunk_data.get('metadata', {})
                                        )
                                        yield response
                                        
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"流式聊天失败: {e}")
            raise
    
    def retrieve_chat(self, conversation_id: str, message_id: Optional[str] = None) -> List[Message]:
        """检索聊天内容"""
        params = {'conversation_id': conversation_id}
        if message_id:
            params['message_id'] = message_id
        
        result = self._make_request('GET', 'chat/retrieve', params=params)
        
        messages = []
        for msg_data in result.get('messages', []):
            message = Message(
                role=MessageRole(msg_data['role']),
                content=msg_data['content'],
                timestamp=msg_data.get('timestamp', time.time()),
                message_id=msg_data.get('message_id'),
                metadata=msg_data.get('metadata', {})
            )
            messages.append(message)
        
        return messages
    
    def list_bots(self) -> List[Dict[str, Any]]:
        """列出可用的机器人"""
        result = self._make_request('GET', 'bots')
        return result.get('bots', [])
    
    def get_bot_info(self, bot_id: str) -> Dict[str, Any]:
        """获取机器人信息"""
        result = self._make_request('GET', f'bots/{bot_id}')
        return result
    
    def upload_file(self, file_path: str, bot_id: str) -> Dict[str, Any]:
        """上传文件"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {
                'Authorization': f'Bearer {self._get_access_token()}'
            }
            
            url = f"{self.coze_config.base_url}/{self.coze_config.api_version}/files/upload"
            
            response = requests.post(url, headers=headers, files=files,
                                   data={'bot_id': bot_id},
                                   timeout=self.coze_config.timeout)
            response.raise_for_status()
            
            return response.json()
    
    def create_dataset(self, name: str, description: str = "") -> Dict[str, Any]:
        """创建数据集"""
        data = {
            'name': name,
            'description': description
        }
        result = self._make_request('POST', 'datasets', data)
        return result
    
    def add_dataset_document(self, dataset_id: str, content: str, 
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """添加数据集文档"""
        data = {
            'content': content,
            'metadata': metadata or {}
        }
        result = self._make_request('POST', f'datasets/{dataset_id}/documents', data)
        return result
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            self._make_request('GET', 'health')
            return True
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False


class CozeAPIError(Exception):
    """Coze API错误"""
    
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(f"Coze API错误 ({code}): {message}")


class AsyncCozeAPIClient:
    """异步Coze API客户端"""
    
    def __init__(self):
        self.config = get_config()
        self.coze_config = self.config.coze
        self.auth_manager = get_auth_manager()
        self._session: Optional[aiohttp.ClientSession] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        current_time = time.time()
        
        if self._access_token and current_time < self._token_expires_at:
            return self._access_token
        
        logger.info("获取新的访问令牌")
        
        jwt_token = self.auth_manager.create_jwt_token(
            user_id="system",
            tenant_id="default",
            scope=["coze_api"]
        )
        
        auth_token = self.auth_manager.exchange_access_token(jwt_token)
        self._access_token = auth_token.access_token
        self._token_expires_at = auth_token.expires_at
        
        return self._access_token
    
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """异步流式聊天"""
        data = {
            'bot_id': request.bot_id,
            'query': request.query,
            'stream': True
        }
        
        if request.conversation_id:
            data['conversation_id'] = request.conversation_id
        
        if request.context:
            data['context'] = request.context
        
        url = f"{self.coze_config.base_url}/{self.coze_config.api_version}/chat"
        headers = {
            'Authorization': f'Bearer {await self._get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with self._session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data_str)
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                choice = chunk_data['choices'][0]
                                delta = choice.get('delta', {})
                                
                                if 'content' in delta:
                                    response = ChatResponse(
                                        conversation_id=chunk_data.get('conversation_id', ''),
                                        message_id=chunk_data.get('message_id', ''),
                                        content=delta['content'],
                                        role=MessageRole.ASSISTANT,
                                        timestamp=time.time(),
                                        metadata=chunk_data.get('metadata', {})
                                    )
                                    yield response
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"异步流式聊天失败: {e}")
            raise


# 全局客户端实例
_sync_client: Optional[CozeAPIClient] = None


def get_coze_client() -> CozeAPIClient:
    """获取同步Coze客户端"""
    global _sync_client
    if _sync_client is None:
        _sync_client = CozeAPIClient()
    return _sync_client


async def get_async_coze_client() -> AsyncCozeAPIClient:
    """获取异步Coze客户端"""
    return AsyncCozeAPIClient()