"""
宏河書房 Flask 应用入口。
只负责：创建 app → 挂扩展 → 注册蓝图 → 启动种子。
业务逻辑在 routes/、models/、helpers.py 各自维护。
"""
import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from extensions import db
from seed import init_db

# --------------------------------------------------------------------------
# App factory
# --------------------------------------------------------------------------
def create_app() -> Flask:
    app = Flask(__name__)
    cors_origins = os.getenv("CORS_ORIGINS", "*").strip()
    if cors_origins == "*":
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:
        origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
        CORS(app, resources={r"/api/*": {"origins": origins}})

    BASE_DIR = os.path.dirname(__file__)
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        # Render PostgreSQL may provide postgres://, which SQLAlchemy 2 expects as postgresql://
        if database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        sqlite_path = os.getenv("SQLITE_PATH", os.path.join(BASE_DIR, "site.db")).strip()
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + sqlite_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from routes.public import bp as public_bp
    from routes.admin import bp as admin_bp, UPLOAD_DIR
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # Upload file serving (outside blueprint so URL is /uploads/* not /api/uploads/*)
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(UPLOAD_DIR, filename)

    # SPA fallback
    dist_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "dist"))

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        index_path = os.path.join(dist_dir, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(dist_dir, "index.html")
        return (
            {"message": "API server running. Frontend not built yet."},
            200,
        )

    with app.app_context():
        init_db()

    return app


# --------------------------------------------------------------------------
# Entry
# --------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0").strip() == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
