"""数据库初始化种子数据。"""
import os

from werkzeug.security import generate_password_hash

from extensions import db
from models import (
    Category, Book, Article, Banner, NavItem, Download, SiteSetting, AdminUser,
)
from helpers import _dumps

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin")
if ADMIN_USER == "admin" and ADMIN_PASS == "admin":
    print("[WARNING] 管理アカウントがデフォルト(admin/admin)です。環境変数 ADMIN_USER/ADMIN_PASS で変更してください。")


def _add_column_if_missing(table_name, column_name, col_type, default_val=None):
    from sqlalchemy import text
    result = db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    existing = [row[1] for row in result]
    if column_name not in existing:
        db.session.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {col_type}")
        )
        # SQLite ALTER TABLE does not apply DEFAULT to existing rows — backfill them
        if default_val is not None:
            db.session.execute(
                text(f"UPDATE {table_name} SET {column_name} = :val WHERE {column_name} IS NULL"),
                {"val": default_val},
            )
        db.session.commit()
        print(f"[init_db] Added column {table_name}.{column_name}")


def init_db():
    db.create_all()

    # 增量迁移：给已有表补上新列
    _add_column_if_missing("book", "sortWeight", "INTEGER DEFAULT 0")
    _add_column_if_missing("book", "featured", "BOOLEAN DEFAULT 0")
    _add_column_if_missing("article", "sortWeight", "INTEGER DEFAULT 0")
    _add_column_if_missing("article", "featured", "BOOLEAN DEFAULT 0")
    _add_column_if_missing("banner", "sortWeight", "INTEGER DEFAULT 0")
    _add_column_if_missing("site_setting", "services", "TEXT DEFAULT '[]'", "[]")
    _add_column_if_missing("site_setting", "clients", "TEXT DEFAULT '[]'", "[]")
    _add_column_if_missing("site_setting", "homeSections", "TEXT DEFAULT '[]'", "[]")
    _add_column_if_missing("site_setting", "logoUrl", "VARCHAR(500) DEFAULT ''")
    _add_column_if_missing("site_setting", "twitterText", "VARCHAR(500) DEFAULT ''", "")
    _add_column_if_missing("site_setting", "businessLead", "TEXT DEFAULT ''", "")
    _add_column_if_missing("site_setting", "businessIntro", "TEXT DEFAULT ''", "")
    _add_column_if_missing("site_setting", "businessNote", "TEXT DEFAULT ''", "")

    if Category.query.count() == 0:
        for c in [
            {"id": "bungaku", "name": "文芸"},
            {"id": "rekishi", "name": "歴史"},
            {"id": "shiso", "name": "思想・哲学"},
            {"id": "minzoku", "name": "民俗・文化"},
        ]:
            db.session.add(Category(**c))

    if Book.query.count() == 0:
        books = [
            {"id": "4908989273", "title": "第１冊（販売中）", "author": "著者名",
             "cover": "", "price": 1800, "isbn": "978-4-908989-27-3",
             "publishDate": "2024-01-01", "category": "bungaku",
             "description": "（占位）最長級歴史推理小説。", "onSale": True,
             "amazonUrl": "https://www.amazon.co.jp"},
            {"id": "1019564", "title": "第２冊（販売中）", "author": "著者名",
             "cover": "", "price": 1800, "isbn": "978-4-908989-27-4",
             "publishDate": "2024-02-01", "category": "bungaku",
             "description": "（占位）最長級歴史推理小説。", "onSale": True,
             "amazonUrl": "https://www.amazon.co.jp"},
            {"id": "532900", "title": "第３冊（販売中）", "author": "著者名",
             "cover": "", "price": 1800, "isbn": "978-4-908989-27-5",
             "publishDate": "2024-03-01", "category": "rekishi",
             "description": "（占位）最長級歴史推理小説。", "onSale": True,
             "amazonUrl": "https://www.amazon.co.jp"},
            {"id": "872804", "title": "第４冊（販売中）", "author": "著者名",
             "cover": "", "price": 1800, "isbn": "978-4-908989-27-6",
             "publishDate": "2024-04-01", "category": "rekishi",
             "description": "（占位）最長級歴史推理小説。", "onSale": True,
             "amazonUrl": "https://www.amazon.co.jp"},
            {"id": "872805", "title": "第５巻（販売中）", "author": "著者名",
             "cover": "", "price": 1800, "isbn": "978-4-908989-27-7",
             "publishDate": "2024-05-01", "category": "shiso",
             "description": "（占位）最長級歴史推理小説。", "onSale": True,
             "amazonUrl": "https://www.amazon.co.jp"},
            {"id": "1019568", "title": "第６冊（販売中）", "author": "著者名",
             "cover": "", "price": 1800, "isbn": "978-4-908989-27-8",
             "publishDate": "2024-06-01", "category": "shiso",
             "description": "（占位）最長級歴史推理小説。", "onSale": True,
             "amazonUrl": "https://www.amazon.co.jp"},
        ]
        for b in books:
            b["relatedIds"] = _dumps(b.get("relatedIds") or [])
            b["sampleImages"] = _dumps(b.get("sampleImages") or [])
            db.session.add(Book(**b))

    if Article.query.count() == 0:
        db.session.add(Article(
            id="a1", title="コラム記事（占位）",
            excerpt="（占位）概要…", cover="", body="（占位）本文…",
            category="bungaku", publishedAt="2024-01-01",
        ))

    if Banner.query.count() == 0:
        db.session.add(Banner(
            id="b1", image="", title="（占位）新刊案内",
            link="/books", order=1, sortWeight=1,
        ))

    if NavItem.query.count() == 0:
        for idx, item in enumerate([
            {"label": "ホーム", "to": "/sy"},
            {"label": "書籍", "to": "/books"},
            {"label": "業務紹介", "to": "/shjs"},
            {"label": "コラム", "to": "/shhy"},
            {"label": "購入について", "to": "/shxw"},
            {"label": "会社概要", "to": "/zpxx"},
            {"label": "お問い合わせ", "to": "/contact"},
            {"label": "ダウンロード", "to": "/information"},
        ], start=1):
            db.session.add(NavItem(
                id=f"nav{idx}", label=item["label"], to=item["to"],
                order=idx, visible=True,
            ))

    if Download.query.count() == 0:
        db.session.add(Download(
            id="d1", name="カタログ（占位）.pdf", url="#",
            size="（占位）2.3MB", description="（占位）説明…",
            publishedAt="2024-01-01",
        ))

    if SiteSetting.query.count() == 0:
        db.session.add(SiteSetting(
            name="株式会社ヒロガワ（宏河書房）",
            intro="宏河書房は「株式会社ヒロガワ」の出版部。中国の文芸・歴史・思想・哲学・文化・民俗などを中心に出版活動を行っています。",
            twitterUrl="https://x.com/Hirogawa_Books",
            twitterText="X ツイッターを利用しています。",
            email="info@hirogawa.com",
            address="（占位）東京都…",
            phone="（占位）03-0000-0000",
            company=_dumps({
                "englishName": "HIROGAWA CO.,LTD.",
                "homepageUrl": "https://www.hirogawa.com",
                "address": "芦屋市南宮町",
                "access": "阪神線打出駅より徒歩〇分、または、JR芦屋駅より徒歩〇分（調整中）",
                "established": "平成28年（2016年）8月",
                "contactOffice": "中国に連絡所を設置",
                "representative": "代表取締役社長：浦 立新",
                "business": "著作権代理業、出版業、及びそれらに関連するコンサルタント。出版業務においては、中国の歴史・思想・哲学・文芸・民俗などを中心に出版活動を行っています。",
            }),
            services=_dumps([
                "中国の現地出版社のニーズに合わせた新刊および既刊のご案内。",
                "中国の現地出版社選びに対するアドバイス。",
                "リクエストへの対応。",
                "オファーの促進および確認、オファーの伝達及び進捗状況の管理。",
                "翻訳許諾契約書草案の作成。",
                "契約前に双方意思への細かな確認。",
                "翻訳許諾契約書の正式締結手続。",
                "前払金を含むロイヤリティーの支払い交渉および管理。",
                "現地での源泉徴収所得税の確認、取得およびその管理。",
                "翻訳版印刷前の表紙などへの確認、翻訳版の発行スケジュール確認、発行後の献本発送などの管理。",
                "売上報告書の管理。",
                "中国で行われる国際ブックフェアへのご案内、現地での様々なサポート業務。",
            ]),
            clients=_dumps([
                "京都大学学術出版会",
                "研文出版",
                "国書刊行会",
                "関西大学出版会",
                "創文社（元）",
                "中国書店",
                "一般社団法人農山漁村文化協会",
                "法藏館",
                "平凡社",
                "PHP研究所",
                "株式会社ペリカン",
                "勉诚出版",
                "北海道大学出版会",
                "ミネルヴァ書房",
                "六一書房",
                "山川出版社",
                "柳原出版社",
            ]),
            homeSections=_dumps([
                {"id": "sec_new", "title": "新刊紹介", "bookId": "4908989273"},
            ]),
            businessLead="近年、日本の作品は中国で注目を集めています。小社は、これからの実績とネットワークを生かし、日本で生まれた作品を中国へご紹介しています。著作権の仲介業務および関連のコンサルタント業務をご提供いたします。",
            businessIntro="小社は、日本の作品の翻訳出版契約締結までのエージェント業務を迅速かつ安心できる著作権の仲介業務および関連のコンサルタント業務をご提供致しております。",
            businessNote="また、日本と中国の出版社間の相互交流を深める目的で関連の文化交流活動の計画と推進を行っております。お気軽にお問い合わせください。",
        ))

    if AdminUser.query.count() == 0:
        db.session.add(AdminUser(
            username=ADMIN_USER,
            password_hash=generate_password_hash(ADMIN_PASS),
        ))

    db.session.commit()
