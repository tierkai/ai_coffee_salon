"""
认证和权限管理器
负责JWT认证、RBAC权限控制和多租户隔离
"""
import jwt
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .config_manager import get_config

logger = logging.getLogger(__name__)


class Permission(Enum):
    """权限枚举"""
    # 知识库权限
    KB_READ = "kb:read"
    KB_WRITE = "kb:write"
    KB_PUBLISH = "kb:publish"
    
    # 检索权限
    SEARCH_READ = "search:read"
    SEARCH_WRITE = "search:write"
    
    # 审稿权限
    REVIEW_READ = "review:read"
    REVIEW_WRITE = "review:write"
    REVIEW_APPROVE = "review:approve"
    
    # 打印权限
    PRINT_READ = "print:read"
    PRINT_WRITE = "print:write"
    
    # 系统权限
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_AUDIT = "system:audit"


class Role(Enum):
    """角色枚举"""
    ADMIN = "admin"
    RESEARCHER = "researcher"
    EVALUATOR = "evaluator"
    SUMMARIZER = "summarizer"
    QNA_AGENT = "qna_agent"
    PRINT_OPERATOR = "print_operator"
    AUDITOR = "auditor"


@dataclass
class User:
    """用户信息"""
    user_id: str
    username: str
    email: str
    tenant_id: str
    roles: Set[Role] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: float = field(default_factory=time.time)
    last_login: Optional[float] = None


@dataclass
class Tenant:
    """租户信息"""
    tenant_id: str
    name: str
    quota: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class AuthToken:
    """认证令牌"""
    access_token: str
    refresh_token: str
    expires_at: float
    user_id: str
    tenant_id: str
    scope: Set[str] = field(default_factory=set)


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.config = get_config()
        self.security_config = self.config.security
        self._users: Dict[str, User] = {}
        self._tenants: Dict[str, Tenant] = {}
        self._tokens: Dict[str, AuthToken] = {}
        self._role_permissions: Dict[Role, Set[Permission]] = self._init_role_permissions()
        
        # 生成密钥对（生产环境中应该从安全存储中加载）
        self._private_key = self._generate_private_key()
        self._public_key = self._private_key.public_key()
    
    def _init_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """初始化角色权限映射"""
        return {
            Role.ADMIN: {
                Permission.KB_READ, Permission.KB_WRITE, Permission.KB_PUBLISH,
                Permission.SEARCH_READ, Permission.SEARCH_WRITE,
                Permission.REVIEW_READ, Permission.REVIEW_WRITE, Permission.REVIEW_APPROVE,
                Permission.PRINT_READ, Permission.PRINT_WRITE,
                Permission.SYSTEM_ADMIN, Permission.SYSTEM_AUDIT
            },
            Role.RESEARCHER: {
                Permission.KB_READ, Permission.KB_WRITE,
                Permission.SEARCH_READ, Permission.SEARCH_WRITE
            },
            Role.EVALUATOR: {
                Permission.KB_READ,
                Permission.SEARCH_READ,
                Permission.REVIEW_READ, Permission.REVIEW_WRITE
            },
            Role.SUMMARIZER: {
                Permission.KB_READ, Permission.KB_WRITE, Permission.KB_PUBLISH,
                Permission.SEARCH_READ,
                Permission.REVIEW_READ, Permission.REVIEW_APPROVE
            },
            Role.QNA_AGENT: {
                Permission.KB_READ,
                Permission.SEARCH_READ
            },
            Role.PRINT_OPERATOR: {
                Permission.PRINT_READ, Permission.PRINT_WRITE
            },
            Role.AUDITOR: {
                Permission.SYSTEM_AUDIT,
                Permission.KB_READ, Permission.REVIEW_READ, Permission.PRINT_READ
            }
        }
    
    def _generate_private_key(self) -> rsa.RSAPrivateKey:
        """生成RSA私钥"""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
    
    def _encode_jwt(self, payload: Dict[str, Any]) -> str:
        """编码JWT令牌"""
        if self.security_config.jwt_algorithm == "RS256":
            private_key_pem = self._private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            return jwt.encode(payload, private_key_pem, algorithm='RS256')
        else:
            return jwt.encode(payload, self.security_config.jwt_secret_key, algorithm='HS256')
    
    def _decode_jwt(self, token: str) -> Dict[str, Any]:
        """解码JWT令牌"""
        try:
            if self.security_config.jwt_algorithm == "RS256":
                public_key_pem = self._public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                return jwt.decode(token, public_key_pem, algorithms=['RS256'])
            else:
                return jwt.decode(token, self.security_config.jwt_secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except jwt.InvalidTokenError:
            raise ValueError("无效令牌")
    
    def create_jwt_token(self, user_id: str, tenant_id: str, scope: List[str] = None) -> str:
        """创建JWT令牌"""
        now = time.time()
        payload = {
            'iss': 'coze-integration',
            'sub': user_id,
            'aud': 'coze-api',
            'iat': now,
            'exp': now + self.security_config.jwt_expiry,
            'tenant_id': tenant_id,
            'scope': scope or [],
            'jti': secrets.token_hex(16)  # 防止重放攻击
        }
        
        return self._encode_jwt(payload)
    
    def exchange_access_token(self, jwt_token: str) -> AuthToken:
        """交换访问令牌"""
        try:
            payload = self._decode_jwt(jwt_token)
            user_id = payload['sub']
            tenant_id = payload['tenant_id']
            
            # 验证用户
            user = self._users.get(user_id)
            if not user or not user.is_active:
                raise ValueError("用户不存在或已禁用")
            
            # 更新最后登录时间
            user.last_login = time.time()
            
            # 生成访问令牌
            access_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)
            expires_at = time.time() + 3600  # 1小时
            
            auth_token = AuthToken(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                user_id=user_id,
                tenant_id=tenant_id,
                scope=set(payload.get('scope', []))
            )
            
            self._tokens[access_token] = auth_token
            
            logger.info(f"为用户 {user_id} 生成访问令牌")
            return auth_token
            
        except Exception as e:
            logger.error(f"令牌交换失败: {e}")
            raise
    
    def verify_access_token(self, token: str) -> Optional[User]:
        """验证访问令牌"""
        auth_token = self._tokens.get(token)
        if not auth_token:
            return None
        
        if time.time() > auth_token.expires_at:
            # 令牌过期，删除
            del self._tokens[token]
            return None
        
        return self._users.get(auth_token.user_id)
    
    def register_user(self, user: User) -> bool:
        """注册用户"""
        if user.user_id in self._users:
            return False
        
        # 设置用户权限（基于角色）
        for role in user.roles:
            user.permissions.update(self._role_permissions.get(role, set()))
        
        self._users[user.user_id] = user
        logger.info(f"注册用户: {user.username} ({user.user_id})")
        return True
    
    def create_tenant(self, tenant: Tenant) -> bool:
        """创建租户"""
        if tenant.tenant_id in self._tenants:
            return False
        
        self._tenants[tenant.tenant_id] = tenant
        logger.info(f"创建租户: {tenant.name} ({tenant.tenant_id})")
        return True
    
    def check_permission(self, user: User, permission: Permission, tenant_id: str = None) -> bool:
        """检查权限"""
        # 检查租户隔离
        if tenant_id and user.tenant_id != tenant_id:
            return False
        
        # 检查用户权限
        return permission in user.permissions
    
    def check_role(self, user: User, role: Role) -> bool:
        """检查角色"""
        return role in user.roles
    
    def get_user_permissions(self, user: User) -> Set[Permission]:
        """获取用户所有权限"""
        return user.permissions.copy()
    
    def get_tenant_users(self, tenant_id: str) -> List[User]:
        """获取租户下所有用户"""
        return [user for user in self._users.values() if user.tenant_id == tenant_id]
    
    def revoke_token(self, token: str) -> bool:
        """撤销令牌"""
        if token in self._tokens:
            del self._tokens[token]
            logger.info(f"撤销令牌: {token[:8]}...")
            return True
        return False
    
    def cleanup_expired_tokens(self):
        """清理过期令牌"""
        now = time.time()
        expired_tokens = [
            token for token, auth_token in self._tokens.items()
            if now > auth_token.expires_at
        ]
        
        for token in expired_tokens:
            del self._tokens[token]
        
        if expired_tokens:
            logger.info(f"清理了 {len(expired_tokens)} 个过期令牌")
    
    def audit_log(self, event_type: str, user_id: str, action: str, resource: str = None, result: str = "success"):
        """审计日志"""
        if not self.config.security.audit_enabled:
            return
        
        audit_record = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'result': result,
            'ip_address': 'unknown',  # 实际实现中应该从请求中获取
            'user_agent': 'unknown'
        }
        
        logger.info(f"AUDIT: {audit_record}")


class PermissionManager:
    """权限管理器"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    def require_permission(self, permission: Permission):
        """权限装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 从上下文获取当前用户（实际实现中应该从请求上下文中获取）
                user = kwargs.get('current_user')
                if not user:
                    raise PermissionError("未认证用户")
                
                if not self.auth_manager.check_permission(user, permission):
                    self.auth_manager.audit_log(
                        "permission_denied",
                        user.user_id,
                        f"尝试访问 {permission.value}",
                        result="denied"
                    )
                    raise PermissionError(f"权限不足: {permission.value}")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_role(self, role: Role):
        """角色装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                user = kwargs.get('current_user')
                if not user:
                    raise PermissionError("未认证用户")
                
                if not self.auth_manager.check_role(user, role):
                    self.auth_manager.audit_log(
                        "role_denied",
                        user.user_id,
                        f"尝试执行需要 {role.value} 角色的操作",
                        result="denied"
                    )
                    raise PermissionError(f"角色不足: {role.value}")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator


# 全局认证管理器实例
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """获取全局认证管理器实例"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


def get_permission_manager() -> PermissionManager:
    """获取权限管理器实例"""
    return PermissionManager(get_auth_manager())