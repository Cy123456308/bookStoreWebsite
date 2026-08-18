"""Admin 认证：数据库持久化 token 与 require_admin 装饰器。"""
from functools import wraps

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify
        from models import AdminToken

        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        if not token:
            return jsonify({"error": "unauthorized"}), 401

        token_row = AdminToken.query.filter_by(token=token).first()
        if token_row is None:
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper
