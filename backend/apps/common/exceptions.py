from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.views import exception_handler


ERROR_CODE_MAP = {
    status.HTTP_400_BAD_REQUEST: 40001,
    status.HTTP_401_UNAUTHORIZED: 40101,
    status.HTTP_403_FORBIDDEN: 40301,
    status.HTTP_404_NOT_FOUND: 40401,
    status.HTTP_409_CONFLICT: 40901,
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    status_code = response.status_code
    code = ERROR_CODE_MAP.get(status_code, 50001)
    message = "服务器错误" if status_code >= 500 else "请求失败"
    errors = response.data

    if isinstance(exc, exceptions.ValidationError):
        message = "参数错误"
    elif isinstance(exc, exceptions.NotAuthenticated):
        message = "未登录"
    elif isinstance(exc, exceptions.PermissionDenied):
        message = "无权限"
    elif isinstance(exc, (exceptions.NotFound, Http404)):
        message = "资源不存在"
    elif isinstance(errors, dict) and "detail" in errors:
        message = str(errors["detail"])

    response.data = {
        "code": code,
        "message": message,
        "errors": errors,
    }
    return response
