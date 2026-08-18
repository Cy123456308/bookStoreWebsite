"""Admin 鉴权 + 写入 API。"""
import os
import io

from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import secrets

from extensions import db
from auth import ACTIVE_TOKENS, require_admin
from models import (
    Book, Article, Category, Banner, NavItem, Download,
    SiteSetting, AdminUser,
)
from helpers import (
    book_to_dict, article_to_dict, banner_to_dict,
    nav_item_to_dict, download_to_dict, site_to_dict,
    _dumps, _new_id,
)

UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"),
)
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
ALLOWED_MIME = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_DIMENSION = 4096  # 单边最大像素

# Expose UPLOAD_DIR and admin_upload for use outside the blueprint
bp = Blueprint("admin", __name__, url_prefix="/api")


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
@bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    user = AdminUser.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    token = secrets.token_hex(32)
    ACTIVE_TOKENS.add(token)
    return jsonify({"token": token})


@bp.route("/admin/logout", methods=["POST"])
@require_admin
def admin_logout():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    ACTIVE_TOKENS.discard(token)
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Upload
# --------------------------------------------------------------------------
@bp.route("/admin/upload", methods=["POST"])
@require_admin
def admin_upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "no file"}), 400

    # 扩展名检查
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"unsupported file type: {ext}"}), 400

    # MIME 类型检查
    if file.content_type and file.content_type not in ALLOWED_MIME:
        return jsonify({"error": f"unsupported MIME type: {file.content_type}"}), 400

    # 文件大小检查
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"file too large: {file_size} bytes (max {MAX_FILE_SIZE} bytes)"}), 400
    if file_size == 0:
        return jsonify({"error": "empty file"}), 400

    # 图片尺寸检查（尝试解析图片）
    try:
        from PIL import Image
        img = Image.open(file)
        img.verify()  # 验证图片完整性
        file.seek(0)
        img = Image.open(file)
        w, h = img.size
        if w > MAX_IMAGE_DIMENSION or h > MAX_IMAGE_DIMENSION:
            return jsonify({"error": f"image too large: {w}x{h} (max {MAX_IMAGE_DIMENSION}px per side)"}), 400
    except ImportError:
        # PIL 未安装，跳过尺寸检查
        pass
    except Exception as e:
        return jsonify({"error": f"invalid image: {str(e)}"}), 400

    filename = f"{secrets.token_hex(8)}{ext}"
    file.save(os.path.join(UPLOAD_DIR, filename))

    public_base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    file_url = f"/uploads/{filename}"
    if public_base_url:
        file_url = f"{public_base_url}{file_url}"

    return jsonify({"url": file_url})


# --------------------------------------------------------------------------
# Entity apply helpers
# --------------------------------------------------------------------------
def _apply_book(data, b):
    b.title = data.get("title", b.title)
    b.author = data.get("author", b.author)
    b.cover = data.get("cover", b.cover)
    b.price = data.get("price", b.price)
    b.isbn = data.get("isbn", b.isbn)
    b.publishDate = data.get("publishDate", b.publishDate)
    b.category = data.get("category", b.category)
    b.description = data.get("description", b.description)
    b.onSale = data.get("onSale", b.onSale)
    b.amazonUrl = data.get("amazonUrl", b.amazonUrl)
    if "relatedIds" in data:
        b.relatedIds = _dumps(data["relatedIds"] or [])
    if "sampleImages" in data:
        b.sampleImages = _dumps(data["sampleImages"] or [])
    if "sortWeight" in data:
        b.sortWeight = data.get("sortWeight", b.sortWeight)
    if "featured" in data:
        b.featured = data.get("featured", b.featured)


def _apply_article(data, a):
    a.title = data.get("title", a.title)
    a.excerpt = data.get("excerpt", a.excerpt)
    a.cover = data.get("cover", a.cover)
    a.body = data.get("body", a.body)
    a.category = data.get("category", a.category)
    a.publishedAt = data.get("publishedAt", a.publishedAt)
    if "sortWeight" in data:
        a.sortWeight = data.get("sortWeight", a.sortWeight)
    if "featured" in data:
        a.featured = data.get("featured", a.featured)


def _apply_banner(data, b):
    b.image = data.get("image", b.image)
    b.title = data.get("title", b.title)
    b.link = data.get("link", b.link)
    b.order = data.get("order", b.order)
    if "sortWeight" in data:
        b.sortWeight = data.get("sortWeight", b.sortWeight)


def _apply_nav_item(data, n):
    n.label = data.get("label", n.label)
    n.to = data.get("to", n.to)
    n.order = data.get("order", n.order)
    if "visible" in data:
        n.visible = data.get("visible", n.visible)


def _apply_download(data, d):
    d.name = data.get("name", d.name)
    d.url = data.get("url", d.url)
    d.size = data.get("size", d.size)
    d.description = data.get("description", d.description)
    d.publishedAt = data.get("publishedAt", d.publishedAt)


def _apply_site(data, s):
    s.name = data.get("name", s.name)
    s.intro = data.get("intro", s.intro)
    s.twitterUrl = data.get("twitterUrl", s.twitterUrl)
    s.email = data.get("email", s.email)
    s.address = data.get("address", s.address)
    s.phone = data.get("phone", s.phone)
    if "company" in data:
        s.company = _dumps(data["company"] or {})
    if "services" in data:
        s.services = _dumps(data["services"] or [])
    if "clients" in data:
        s.clients = _dumps(data["clients"] or [])
    if "homeSections" in data:
        s.homeSections = _dumps(data["homeSections"] or [])
    if "logoUrl" in data:
        s.logoUrl = data.get("logoUrl", s.logoUrl)


# --------------------------------------------------------------------------
# Nav items
# --------------------------------------------------------------------------
@bp.route("/admin/nav", methods=["GET"])
@require_admin
def admin_get_nav():
    items = NavItem.query.order_by(NavItem.order.asc()).all()
    return jsonify([nav_item_to_dict(n) for n in items])


@bp.route("/admin/nav", methods=["POST"])
@require_admin
def admin_create_nav():
    data = request.get_json(silent=True) or {}
    nid = data.get("id") or _new_id("nav")
    if NavItem.query.get(nid):
        return jsonify({"error": "id exists"}), 409
    n = NavItem(id=nid)
    _apply_nav_item(data, n)
    db.session.add(n)
    db.session.commit()
    return jsonify(nav_item_to_dict(n)), 201


@bp.route("/admin/nav/<nav_id>", methods=["PUT"])
@require_admin
def admin_update_nav(nav_id):
    n = NavItem.query.get(nav_id)
    if n is None:
        return jsonify({"error": "not found"}), 404
    _apply_nav_item(request.get_json(silent=True) or {}, n)
    db.session.commit()
    return jsonify(nav_item_to_dict(n))


@bp.route("/admin/nav/<nav_id>", methods=["DELETE"])
@require_admin
def admin_delete_nav(nav_id):
    n = NavItem.query.get(nav_id)
    if n is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(n)
    db.session.commit()
    return jsonify({"ok": True})


@bp.route("/admin/nav/reorder", methods=["PUT"])
@require_admin
def admin_reorder_nav():
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])
    for entry in items:
        n = NavItem.query.get(entry.get("id"))
        if n:
            n.order = entry.get("order", n.order)
    db.session.commit()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Books
# --------------------------------------------------------------------------
@bp.route("/books", methods=["POST"])
@require_admin
def create_book():
    data = request.get_json(silent=True) or {}
    bid = data.get("id") or _new_id("b")
    if Book.query.get(bid):
        return jsonify({"error": "id exists"}), 409
    b = Book(id=bid)
    _apply_book(data, b)
    db.session.add(b)
    db.session.commit()
    return jsonify(book_to_dict(b)), 201


@bp.route("/books/<book_id>", methods=["PUT"])
@require_admin
def update_book(book_id):
    b = Book.query.get(book_id)
    if b is None:
        return jsonify({"error": "not found"}), 404
    _apply_book(request.get_json(silent=True) or {}, b)
    db.session.commit()
    return jsonify(book_to_dict(b))


@bp.route("/books/<book_id>", methods=["DELETE"])
@require_admin
def delete_book(book_id):
    b = Book.query.get(book_id)
    if b is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(b)
    db.session.commit()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Articles
# --------------------------------------------------------------------------
@bp.route("/articles", methods=["POST"])
@require_admin
def create_article():
    data = request.get_json(silent=True) or {}
    aid = data.get("id") or _new_id("a")
    if Article.query.get(aid):
        return jsonify({"error": "id exists"}), 409
    a = Article(id=aid)
    _apply_article(data, a)
    db.session.add(a)
    db.session.commit()
    return jsonify(article_to_dict(a)), 201


@bp.route("/articles/<article_id>", methods=["PUT"])
@require_admin
def update_article(article_id):
    a = Article.query.get(article_id)
    if a is None:
        return jsonify({"error": "not found"}), 404
    _apply_article(request.get_json(silent=True) or {}, a)
    db.session.commit()
    return jsonify(article_to_dict(a))


@bp.route("/articles/<article_id>", methods=["DELETE"])
@require_admin
def delete_article(article_id):
    a = Article.query.get(article_id)
    if a is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(a)
    db.session.commit()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Categories
# --------------------------------------------------------------------------
@bp.route("/categories", methods=["POST"])
@require_admin
def create_category():
    data = request.get_json(silent=True) or {}
    cid = data.get("id") or _new_id("c")
    if Category.query.get(cid):
        return jsonify({"error": "id exists"}), 409
    db.session.add(Category(id=cid, name=data.get("name", "")))
    db.session.commit()
    return jsonify({"id": cid, "name": data.get("name", "")}), 201


@bp.route("/categories/<cat_id>", methods=["PUT"])
@require_admin
def update_category(cat_id):
    c = Category.query.get(cat_id)
    if c is None:
        return jsonify({"error": "not found"}), 404
    c.name = request.get_json(silent=True).get("name", c.name)
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name})


@bp.route("/categories/<cat_id>", methods=["DELETE"])
@require_admin
def delete_category(cat_id):
    c = Category.query.get(cat_id)
    if c is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Banners
# --------------------------------------------------------------------------
@bp.route("/banners", methods=["POST"])
@require_admin
def create_banner():
    data = request.get_json(silent=True) or {}
    bid = data.get("id") or _new_id("bn")
    if Banner.query.get(bid):
        return jsonify({"error": "id exists"}), 409
    b = Banner(id=bid)
    _apply_banner(data, b)
    db.session.add(b)
    db.session.commit()
    return jsonify(banner_to_dict(b)), 201


@bp.route("/banners/<banner_id>", methods=["PUT"])
@require_admin
def update_banner(banner_id):
    b = Banner.query.get(banner_id)
    if b is None:
        return jsonify({"error": "not found"}), 404
    _apply_banner(request.get_json(silent=True) or {}, b)
    db.session.commit()
    return jsonify(banner_to_dict(b))


@bp.route("/banners/<banner_id>", methods=["DELETE"])
@require_admin
def delete_banner(banner_id):
    b = Banner.query.get(banner_id)
    if b is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(b)
    db.session.commit()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Downloads
# --------------------------------------------------------------------------
@bp.route("/downloads", methods=["POST"])
@require_admin
def create_download():
    data = request.get_json(silent=True) or {}
    did = data.get("id") or _new_id("d")
    if Download.query.get(did):
        return jsonify({"error": "id exists"}), 409
    d = Download(id=did)
    _apply_download(data, d)
    db.session.add(d)
    db.session.commit()
    return jsonify(download_to_dict(d)), 201


@bp.route("/downloads/<download_id>", methods=["PUT"])
@require_admin
def update_download(download_id):
    d = Download.query.get(download_id)
    if d is None:
        return jsonify({"error": "not found"}), 404
    _apply_download(request.get_json(silent=True) or {}, d)
    db.session.commit()
    return jsonify(download_to_dict(d))


@bp.route("/downloads/<download_id>", methods=["DELETE"])
@require_admin
def delete_download(download_id):
    d = Download.query.get(download_id)
    if d is None:
        return jsonify({"error": "not found"}), 404
    db.session.delete(d)
    db.session.commit()
    return jsonify({"ok": True})


# --------------------------------------------------------------------------
# Site / Company
# --------------------------------------------------------------------------
@bp.route("/site", methods=["PUT"])
@require_admin
def put_site():
    s = SiteSetting.query.first()
    if s is None:
        s = SiteSetting(id=1)
        db.session.add(s)
    _apply_site(request.get_json(silent=True) or {}, s)
    db.session.commit()
    return jsonify(site_to_dict(s))
