# Sakura + Render 部署指南（前后端分离）

如果你准备把后端迁移到 PHP（Laravel），请参考：
- [BACKEND_PHP_MIGRATION_GUIDE.md](BACKEND_PHP_MIGRATION_GUIDE.md)

本项目建议部署方式：
- 前端（Vue/Vite）部署到 Sakura（静态站点）
- 后端（Flask）部署到 Render（Web Service）

## 1. 后端部署到 Render

### 1.1 新建服务
1. 登录 Render Dashboard。
2. New + -> Web Service。
3. 选择本项目仓库。
4. Root Directory 填写 `backend`。
5. Runtime 选择 `Python 3`。

### 1.2 构建与启动命令
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
gunicorn app:app
```

### 1.3 环境变量（按需）
参考 `backend/.env.render.example`：
- `CORS_ORIGINS=https://你的前端域名`
- `PUBLIC_BASE_URL=https://你的-render-服务.onrender.com`
- `UPLOAD_DIR=/var/data/uploads`
- `SQLITE_PATH=/var/data/site.db`（如果用 SQLite）
- `FLASK_DEBUG=0`

### 1.4 持久化（重要）
如果继续使用 SQLite 和上传文件，必须使用 Render Persistent Disk：
1. 在服务里添加 Persistent Disk（建议挂载到 `/var/data`）。
2. 保持：
   - `SQLITE_PATH=/var/data/site.db`
   - `UPLOAD_DIR=/var/data/uploads`

否则重启/重新部署后数据库和上传文件会丢失。

## 2. 前端部署到 Sakura

### 2.1 配置生产 API 地址
在 `frontend` 目录创建 `.env.production`（可从 `.env.production.example` 复制）：

```env
VITE_API_BASE=https://你的-render-服务.onrender.com/api
```

### 2.2 本地打包
在 `frontend` 目录执行：

```bash
npm install
npm run build
```

打包产物在 `frontend/dist`。

### 2.3 上传文件到 Sakura
将 `frontend/dist` 内的所有文件上传到 Sakura 网站根目录（例如 `www`）。

### 2.4 SPA 路由回退
项目已提供 `frontend/public/.htaccess`，构建后会进入 `dist`。上传后可支持 Vue Router history 模式刷新不 404。

## 3. 已做的代码改动

- `backend/app.py`
  - 支持 `PORT`（Render 需要）。
  - 支持 `CORS_ORIGINS`（跨域白名单）。
  - 支持 `DATABASE_URL` 或 `SQLITE_PATH`（数据库可配置）。
- `backend/routes/admin.py`
  - 支持 `UPLOAD_DIR`（上传目录可配置）。
  - 支持 `PUBLIC_BASE_URL`（上传返回绝对 URL）。
- `backend/requirements.txt`
  - 新增 `gunicorn`（生产启动）。
  - 新增 `Pillow`（图片校验能力）。
- `frontend/src/api/index.ts`
  - 增加资源 URL 归一化，处理 `/uploads/...` 在分域部署下的可访问性。
- `frontend/src/env.d.ts`
  - 增加 `VITE_API_BASE` 类型声明。

## 4. 部署后自检

1. 打开前端首页，检查是否能正常拉取站点信息。
2. 打开书籍列表，检查封面图片是否正常加载。
3. 后台登录后上传图片，检查是否显示、保存、刷新后仍可访问。
4. 刷新非首页路由（如 `/books`），确认不 404。
