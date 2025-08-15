import sys
from typing import Optional, Dict, Any

class CustomException(Exception):
    """Base custom exception class with detailed error information"""
    def __init__(
        self,
        message: str,
        error_detail: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_detail = error_detail
        self.context = context or {}
        self.error_location = self._get_error_location()
        super().__init__(self._format_error_message())

    def _get_error_location(self) -> Dict[str, str]:
        """Get file, line number, and function where exception occurred"""
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return {
            'file': exc_tb.tb_frame.f_code.co_filename if exc_tb else 'unknown',
            'line': exc_tb.tb_lineno if exc_tb else 'unknown',
            'function': exc_tb.tb_frame.f_code.co_name if exc_tb else 'unknown'
        }

    def _format_error_message(self) -> str:
        """Format detailed error message"""
        parts = [
            f"Message: {self.message}",
            f"Error: {str(self.error_detail)}" if self.error_detail else "",
            f"Location: {self.error_location['file']}:{self.error_location['line']}",
            f"Function: {self.error_location['function']}"
        ]
        if self.context:
            parts.append(f"Context: {self.context}")
        return " | ".join(filter(None, parts))

    def __str__(self):
        return self._format_error_message()

class ConfigError(CustomException):
    """Specialized exception for configuration errors"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Configuration Error: {message}",
            context=context
        )

class RecommendationError(CustomException):
    """Specialized exception for anime recommendation failures"""
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        model: Optional[str] = None,
        error_detail: Optional[Exception] = None
    ):
        context = {
            'query': query,
            'model': model,
            'service': 'Anime Recommendation'
        }
        super().__init__(
            message=f"Recommendation Error: {message}",
            error_detail=error_detail,
            context=context
        )

class APIError(CustomException):
    """Exception for API-related failures"""
    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        error_detail: Optional[Exception] = None
    ):
        context = {
            'endpoint': endpoint,
            'status_code': status_code
        }
        super().__init__(
            message=f"API Error: {message}",
            error_detail=error_detail,
            context=context
        )
