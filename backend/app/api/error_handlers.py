"""全局错误处理模块 - 统一 API 错误响应，避免信息泄漏"""
from __future__ import annotations

import logging
import traceback
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# 统一的错误响应格式
class ErrorResponse:
    """标准错误响应"""
    
    @staticmethod
    def create(
        status_code: int,
        error_type: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """创建标准错误响应
        
        Args:
            status_code: HTTP 状态码
            error_type: 错误类型标识
            message: 用户友好的错误信息
            details: 额外的错误详情（仅开发环境）
            
        Returns:
            标准错误响应字典
        """
        response = {
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code,
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return response


# 错误处理函数
async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理请求验证错误"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.create(
            status_code=422,
            error_type="validation_error",
            message="请求参数验证失败，请检查输入数据格式",
        ),
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理 HTTP 异常"""
    from fastapi import HTTPException
    
    if isinstance(exc, HTTPException):
        # 对于 4xx 错误，返回安全的错误信息
        if exc.status_code < 500:
            logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse.create(
                    status_code=exc.status_code,
                    error_type="client_error",
                    message=str(exc.detail),
                ),
            )
        # 对于 5xx 错误，隐藏详细信息
        else:
            logger.error(f"HTTP {exc.status_code}: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse.create(
                    status_code=exc.status_code,
                    error_type="server_error",
                    message="服务器内部错误，请稍后重试",
                ),
            )
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create(
            status_code=500,
            error_type="unknown_error",
            message="未知错误",
        ),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的通用异常"""
    # 记录详细的错误信息到日志（包含堆栈跟踪）
    logger.error(
        f"Unhandled exception: {exc}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    # 返回安全的错误信息给客户端
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create(
            status_code=500,
            error_type="internal_error",
            message="服务器内部错误，请稍后重试或联系技术支持",
        ),
    )


async def database_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理数据库异常"""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create(
            status_code=500,
            error_type="database_error",
            message="数据操作失败，请稍后重试",
        ),
    )


async def llm_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理 LLM 服务异常"""
    logger.error(f"LLM service error: {exc}")
    return JSONResponse(
        status_code=503,
        content=ErrorResponse.create(
            status_code=503,
            error_type="llm_service_error",
            message="AI 服务暂时不可用，请稍后重试",
        ),
    )


# 注册所有错误处理器
def register_error_handlers(app):
    """注册全局错误处理器到 FastAPI 应用
    
    Args:
        app: FastAPI 应用实例
    """
    from fastapi.exceptions import RequestValidationError
    from fastapi import HTTPException
    from sqlalchemy.exc import SQLAlchemyError
    
    # 请求验证错误
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # HTTP 异常
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 数据库异常
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    # LLM 相关异常
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers registered successfully")
