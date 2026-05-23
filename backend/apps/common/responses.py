from rest_framework.response import Response


def success_response(data=None, message="success", status=None):
    return Response(
        {
            "code": 0,
            "message": message,
            "data": {} if data is None else data,
        },
        status=status,
    )


def error_response(code=40001, message="参数错误", errors=None, status=400):
    return Response(
        {
            "code": code,
            "message": message,
            "errors": {} if errors is None else errors,
        },
        status=status,
    )
