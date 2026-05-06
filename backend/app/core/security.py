"""安全工具模块 - 提供数据脱敏、输入验证等安全功能"""
from __future__ import annotations

import re


def redact_sensitive_data(text: str | None, max_length: int = 50) -> str:
    """对敏感数据进行脱敏处理
    
    Args:
        text: 原始文本
        max_length: 日志中显示的最大长度
        
    Returns:
        脱敏后的文本，只显示长度信息和前几个字符
    """
    if text is None:
        return "<None>"
    
    if len(text) <= max_length:
        return f"<len={len(text)}>"
    
    return f"<len={len(text)}, preview={text[:20]}...>"


def sanitize_for_log(**kwargs) -> dict:
    """将字典中的敏感字段进行脱敏处理
    
    自动识别并脱敏以下类型字段:
    - 包含 text、content、raw 的字段（可能包含大段文本）
    - 包含 password、secret、key、token 的字段（凭证信息）
    - 包含 email、phone 的字段（联系方式）
    
    Args:
        **kwargs: 需要脱敏的键值对
        
    Returns:
        脱敏后的字典
    """
    sensitive_patterns = [
        r"password",
        r"secret",
        r"api_key",
        r"token",
        r"credential",
    ]
    
    large_text_patterns = [
        r"raw_text",
        r"content",
        r"text",
        r"description",
        r"body",
    ]
    
    contact_patterns = [
        r"email",
        r"phone",
        r"mobile",
    ]
    
    result = {}
    for key, value in kwargs.items():
        key_lower = key.lower()
        
        # 检查是否是凭证类敏感信息
        if any(re.search(pattern, key_lower) for pattern in sensitive_patterns):
            result[key] = "<REDACTED>"
        # 检查是否是联系信息
        elif any(re.search(pattern, key_lower) for pattern in contact_patterns):
            result[key] = redact_contact_info(str(value))
        # 检查是否是大段文本
        elif any(re.search(pattern, key_lower) for pattern in large_text_patterns):
            if isinstance(value, str) and len(value) > 100:
                result[key] = redact_sensitive_data(value)
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


def redact_contact_info(text: str) -> str:
    """对联系信息进行脱敏
    
    - 手机号: 138****8888
    - 邮箱: zh***@example.com
    """
    if not text:
        return text
    
    # 手机号脱敏
    text = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', text)
    
    # 邮箱脱敏
    text = re.sub(r'(\w{2})\w+(@\w+)', r'\1***\2', text)
    
    return text


def validate_safe_pattern(pattern: str) -> str:
    """验证并转义正则表达式模式，防止 ReDoS 攻击
    
    Args:
        pattern: 用户提供的正则表达式模式
        
    Returns:
        安全的转义后的模式
        
    Raises:
        ValueError: 如果模式包含危险特性
    """
    if not pattern or not isinstance(pattern, str):
        raise ValueError("Pattern must be a non-empty string")
    
    # 检查模式长度，防止超长模式导致性能问题
    if len(pattern) > 1000:
        raise ValueError("Pattern too long (max 1000 characters)")
    
    # 转义特殊字符，防止注入
    safe_pattern = re.escape(pattern)
    
    return safe_pattern
