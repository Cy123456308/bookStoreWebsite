# 后端改为 PHP（Laravel）迁移与部署指南

本文用于把当前项目从 Python 后端迁移为 PHP 后端，并优先部署在 Sakura。

## 1. 目标与原则

- 前端保持不变：继续使用 Vue/Vite。
- API 路径尽量不变：沿用 /api 前缀与现有字段。
- 迁移方式：先搭建 Laravel 新后端，再逐步替换现有 Python 接口。
- 上线策略：并行联调，确认功能一致后再切流。

## 2. 推荐目录结构

建议在当前仓库新增目录：

- frontend: 现有前端
- backend_python: 现有 Python 后端（保留作为对照）
- backend_php: 新 Laravel 后端

## 3. 在本地创建 Laravel 后端

### 3.1 初始化项目

在仓库根目录执行：

```bash
composer create-project laravel/laravel backend_php
```

### 3.2 基础配置

在 backend_php/.env 中配置：

- APP_NAME
- APP_ENV=production（上线时）
- APP_URL=你的域名
- DB_CONNECTION=mysql
- DB_HOST / DB_PORT / DB_DATABASE / DB_USERNAME / DB_PASSWORD

### 3.3 必要能力

- 鉴权：建议 Laravel Sanctum 或自定义 Bearer Token 表。
- 文件上传：使用 storage/app/public 或 public/uploads。
- CORS：允许前端域名访问（若前后端分域）。

## 4. 数据模型迁移（按当前项目）

需要建立以下表：

- admin_users
- admin_tokens（或 Sanctum 表）
- categories
- books
- articles
- banners
- downloads
- nav_items
- site_settings

关键字段建议与当前前端一致：

- books.category 使用分类 id（字符串）
- books.onSale、books.featured
- books.sortWeight
- site_settings.services、clients、homeSections 可用 JSON
- site_settings.twitterText、businessLead、businessIntro、businessNote

## 5. API 对照清单（必须兼容）

### 5.1 公开接口

- GET /api/site
- GET /api/banners
- GET /api/categories
- GET /api/categories/usage
- GET /api/books
- GET /api/books/{id}
- GET /api/articles
- GET /api/articles/{id}
- GET /api/downloads
- GET /api/nav
- POST /api/contact

### 5.2 管理接口

- POST /api/admin/login
- POST /api/admin/logout
- POST /api/admin/upload
- POST /api/books
- PUT /api/books/{id}
- DELETE /api/books/{id}
- POST /api/categories
- PUT /api/categories/{id}
- DELETE /api/categories/{id}
- 其余 article、banner、download、site、nav 的增删改查接口

### 5.3 返回结构要求

- 错误保持：{ "error": "..." }
- 分页保持：items、total、page、pageSize
- 上传返回：{ "url": "/uploads/xxx" } 或完整 URL

## 6. 与前端对接注意事项

- 前端环境变量：VITE_API_BASE 指向 PHP API 域名。
- 保持字段命名风格一致（驼峰/下划线统一）。
- 类别删除规则：仅允许删除 bookCount=0 的类型。

## 7. Sakura 部署 Laravel 要点

### 7.1 服务器能力确认

在 Sakura 控制台确认：

- PHP 版本（建议 8.2+）
- 已启用扩展：pdo_mysql、mbstring、openssl、tokenizer、xml、ctype、json、fileinfo
- 可配置站点根目录到 Laravel 的 public

### 7.2 部署步骤

1. 上传 backend_php 代码到服务器。
2. 设置站点根目录为 backend_php/public。
3. 配置 .env 生产参数。
4. 执行：

```bash
php artisan key:generate
php artisan migrate --force
php artisan storage:link
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

5. 给 storage 与 bootstrap/cache 写权限。

### 7.3 前端部署

- frontend 执行 npm run build。
- 上传 dist 到 Sakura 对应站点目录。
- 保留 .htaccess 以支持前端路由回退。

## 8. 切换上线建议

- 阶段 1：前端仍指向 Python，PHP 仅自测。
- 阶段 2：前端灰度指向 PHP，校验核心功能。
- 阶段 3：全量切换到 PHP，保留 Python 作为回退。

## 9. 验收清单

- 后台登录、登出正常。
- 书籍新增、编辑、删除正常。
- 书籍分类新增与删除规则正常。
- 书籍封面上传与展示正常。
- 业务页与公司页可编辑字段可保存。
- 刷新页面后数据不丢失。

## 10. 常见问题

- 全部显示 0 冊：检查 /api/categories/usage 是否返回真实 bookCount。
- 编辑提示 unauthorized：检查 token 机制与登录态。
- 上传成功但图片不显示：检查上传目录映射与返回 URL。
