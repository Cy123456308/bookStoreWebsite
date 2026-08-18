"""公开只读 API。"""
from flask import Blueprint, jsonify, request

from models import Book, Article, Banner, Category, NavItem, Download, SiteSetting
from helpers import (
    book_to_dict, article_to_dict, banner_to_dict,
    nav_item_to_dict, download_to_dict, site_to_dict,
    paginate, _dumps,
)

bp = Blueprint("public", __name__, url_prefix="/api")


@bp.route("/site", methods=["GET"])
def get_site():
    s = SiteSetting.query.first()
    return jsonify(site_to_dict(s) if s else {})


@bp.route("/banners", methods=["GET"])
def get_banners():
    items = Banner.query.order_by(Banner.sortWeight.asc()).all()
    return jsonify([banner_to_dict(b) for b in items])


@bp.route("/categories", methods=["GET"])
def get_categories():
    return jsonify([{"id": c.id, "name": c.name} for c in Category.query.all()])


@bp.route("/categories/usage", methods=["GET"])
def get_categories_usage():
    categories = Category.query.order_by(Category.name.asc()).all()
    result = []
    for c in categories:
        count = Book.query.filter_by(category=c.id).count()
        result.append({"id": c.id, "name": c.name, "bookCount": count})
    return jsonify(result)


@bp.route("/books", methods=["GET"])
def get_books():
    items = Book.query
    category = request.args.get("category")
    on_sale = request.args.get("onSale")
    featured = request.args.get("featured")
    q = (request.args.get("q") or "").strip().lower()
    if category:
        items = items.filter(Book.category == category)
    if on_sale == "true":
        items = items.filter(Book.onSale == True)  # noqa: E712
    if featured == "true":
        items = items.filter(Book.featured == True)  # noqa: E712
    if q:
        from extensions import db
        items = items.filter(
            db.or_(
                Book.title.ilike(f"%{q}%"),
                Book.author.ilike(f"%{q}%"),
            )
        )
    items = items.order_by(Book.sortWeight.desc()).all()
    return jsonify(paginate(
        [book_to_dict(b) for b in items],
        request.args.get("page", type=int),
        request.args.get("pageSize", type=int),
    ))


@bp.route("/books/<book_id>", methods=["GET"])
def get_book(book_id):
    b = Book.query.get(book_id)
    if b is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(book_to_dict(b))


@bp.route("/articles", methods=["GET"])
def get_articles():
    items = Article.query
    featured = request.args.get("featured")
    if featured == "true":
        items = items.filter(Article.featured == True)  # noqa: E712
    items = items.order_by(
        Article.sortWeight.desc(), Article.publishedAt.desc()
    ).all()
    return jsonify(paginate(
        [article_to_dict(a) for a in items],
        request.args.get("page", type=int),
        request.args.get("pageSize", type=int),
    ))


@bp.route("/articles/<article_id>", methods=["GET"])
def get_article(article_id):
    a = Article.query.get(article_id)
    if a is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(article_to_dict(a))


@bp.route("/downloads", methods=["GET"])
def get_downloads():
    return jsonify([download_to_dict(d) for d in Download.query.all()])


@bp.route("/nav", methods=["GET"])
def get_nav():
    items = NavItem.query.filter_by(visible=True).order_by(
        NavItem.order.asc()
    ).all()
    return jsonify([nav_item_to_dict(n) for n in items])


@bp.route("/contact", methods=["POST"])
def post_contact():
    # TODO: 实际发送邮件 / 持久化
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "received": data}), 201
