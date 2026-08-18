"""Admin 认证：token 内网内存管理与 require_admin 装饰器。"""
from functools import wraps

# 有效 token（内存管理・重启后失效）
ACTIVE_TOKENS = set()


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        if not token or token not in ACTIVE_TOKENS:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper
