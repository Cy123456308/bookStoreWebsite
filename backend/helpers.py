"""跨模块共用的纯工具函数。"""
import json
import secrets

from models import (
    Book, Article, Banner, NavItem, Download, SiteSetting,
)


def _loads(text, default):
    if not text:
        return default
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def _dumps(value):
    return json.dumps(value, ensure_ascii=False)


def _new_id(prefix: str) -> str:
    return f"{prefix}{secrets.token_hex(6)}"


# --------------------------------------------------------------------------
# Entity → dict
# --------------------------------------------------------------------------
def book_to_dict(b: Book) -> dict:
    return {
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "cover": b.cover,
        "price": b.price,
        "isbn": b.isbn,
        "publishDate": b.publishDate,
        "category": b.category,
        "description": b.description,
        "onSale": b.onSale,
        "amazonUrl": b.amazonUrl,
        "relatedIds": _loads(b.relatedIds, []),
        "sampleImages": _loads(b.sampleImages, []),
        "sortWeight": b.sortWeight,
        "featured": b.featured,
    }


def article_to_dict(a: Article) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "excerpt": a.excerpt,
        "cover": a.cover,
        "body": a.body,
        "category": a.category,
        "publishedAt": a.publishedAt,
        "sortWeight": a.sortWeight,
        "featured": a.featured,
    }


def banner_to_dict(b: Banner) -> dict:
    return {
        "id": b.id,
        "image": b.image,
        "title": b.title,
        "link": b.link,
        "order": b.order,
        "sortWeight": b.sortWeight,
    }


def nav_item_to_dict(n: NavItem) -> dict:
    return {
        "id": n.id,
        "label": n.label,
        "to": n.to,
        "order": n.order,
        "visible": n.visible,
    }


def download_to_dict(d: Download) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "url": d.url,
        "size": d.size,
        "description": d.description,
        "publishedAt": d.publishedAt,
    }


def site_to_dict(s: SiteSetting) -> dict:
    return {
        "name": s.name,
        "intro": s.intro,
        "twitterUrl": s.twitterUrl,
        "email": s.email,
        "address": s.address,
        "phone": s.phone,
        "company": _loads(s.company, {}),
        "services": _loads(s.services, []),
        "clients": _loads(s.clients, []),
        "homeSections": _loads(s.homeSections, []),
        "logoUrl": s.logoUrl,
    }


def paginate(items: list, page, page_size) -> dict:
    page = max(1, page or 1)
    page_size = min(100, max(1, page_size or 20))
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": len(items),
        "page": page,
        "pageSize": page_size,
    }
