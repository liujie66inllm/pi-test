# AGENTS.md

本文件为在此仓库中工作的 AI 编码代理提供项目指引。内容基于对整个代码库的通读整理。

## 项目概览

一个 Django Web 应用：贪吃蛇小游戏 + 用户账户系统（注册 / 登录 / 个人中心 / 最高分记录）。

- 语言 / 框架：Python 3.13，Django 6.1.1
- 数据库：Supabase 托管 PostgreSQL（原为 SQLite，已迁移）
- 依赖：`requirements.txt`（`Django==6.1.1`、`psycopg[binary]==3.3.5`、`python-dotenv==1.2.1`）
- 前端：Bootstrap 5.3.3（CDN 引入），无自定义 JS/CSS 文件
- 语言环境：`LANGUAGE_CODE='zh-hans'`、`TIME_ZONE='Asia/Shanghai'`、`USE_TZ=True`

## 目录结构

```
.
├── manage.py                 # Django 命令行入口
├── config/                   # 项目配置
│   ├── settings.py           # 核心配置（DB / 认证 / 国际化等）
│   ├── urls.py               # 根路由：admin + accounts
│   ├── wsgi.py / asgi.py     # 标准部署入口（无自定义逻辑）
├── accounts/                 # 用户账户应用（唯一的业务 app）
│   ├── models.py             # Profile（OneToOne 关联内置 User）
│   ├── forms.py              # RegisterForm（基于 UserCreationForm）
│   ├── views.py              # 函数式视图（无类视图）
│   ├── urls.py               # 6 条路由
│   ├── admin.py              # Profile 后台注册
│   ├── apps.py               # AccountsConfig
│   ├── tests.py              # 空文件（仅有 import，无测试）
│   ├── migrations/0001_initial.py  # 唯一迁移，建 Profile 表
│   └── templates/accounts/   # base / index / register / login / home
├── snake_game.py             # 独立桌面贪吃蛇（turtle 图形界面）
├── .env                      # 真实 Supabase 凭据（敏感，勿提交）
├── .env.example              # 环境变量模板
├── .gitignore                # 排除 .env / db.sqlite3 / __pycache__ 等
├── PLAN.md                   # 数据库迁移计划（历史文档）
├── .agents/skills/           # 项目级 Agent 技能（playwright-cli）
└── .pi/                      # Pi 编码代理自身配置/node_modules（非项目代码）
```

## 环境搭建与运行

```bash
pip install -r requirements.txt
cp .env.example .env          # 填入真实 Supabase 连接信息
python manage.py migrate
python manage.py runserver
```

常用命令：

```bash
python manage.py migrate            # 应用迁移
python manage.py makemigrations     # 生成迁移
python manage.py createsuperuser    # 创建管理员
python manage.py test               # 运行测试（当前无任何测试）
python snake_game.py                # 本地贪吃蛇（turtle 图形窗口，与 Django 解耦）
```

## 路由与 URL 命名

根 `config/urls.py` 包含 `admin/` 与 `accounts.urls`。`accounts/urls.py` 定义的命名路由：

| name | 路径 | 视图 | 说明 |
|---|---|---|---|
| `index` | `/` | `index` | 落地页 |
| `register` | `/register/` | `register` | 注册（成功后自动登录并跳转 home） |
| `login` | `/login/` | `login_view` | 登录 |
| `logout` | `/logout/` | `logout_view` | 退出 |
| `home` | `/home/` | `home` | 个人中心（`@login_required`） |
| `update_score` | `/update-score/` | `update_score` | POST 提交分数（`@login_required`） |

认证相关设置：`LOGIN_URL='login'`、`LOGIN_REDIRECT_URL='home'`、`LOGOUT_REDIRECT_URL='login'`。

## 数据模型

- 认证使用 Django 内置 `User` 模型（`AUTH_USER_MODEL` 未自定义）。
- `accounts.models.Profile`：
  - `user`：`OneToOneField(User, related_name='profile')`
  - `high_score`：`IntegerField(default=0)`（贪吃蛇最高分）
  - `created_at`：`DateTimeField(auto_now_add=True)`
- 通过 `post_save` 信号：新建 User 时自动创建 Profile，保存 User 时同步保存 Profile。
- `ProfileAdmin`（`admin.py`）：列表展示 `user / high_score / created_at`，可按用户名/邮箱搜索。

## 视图与业务逻辑

- **register**：`RegisterForm`（`UserCreationForm` 子类），新增必填 `email` 并做唯一性校验；已登录用户访问会重定向 home。
- **login_view**：手动读取 `username`/`password` 字段调用 `authenticate`（未使用 Django 的 AuthenticationForm）。
- **update_score**：POST 读取 `score`（`int`，异常时置 0），仅当大于 `profile.high_score` 时更新；否则仅提示。提交后重定向 home。
- 视图全部为函数式视图，用 `django.contrib.messages` 做用户反馈。

## 模板要点

- `base.html` 为唯一基模板：Bootstrap 5.3.3 CDN、深色导航栏（按登录态显示不同按钮）、消息 alert 区、页脚。子模板通过 `{% extends %}` + `{% block title/content %}` 继承。
- `home.html`：展示用户名/邮箱/最高分/注册时间，含提交分数的表单（`action="{% url 'update_score' %}"`，带 CSRF token）。
- `register.html`：遍历 `form` 字段，展示 `help_text`（`|safe`）与逐字段错误。
- `login.html`：手写表单（`username`/`password`），非 Django form。

## 数据库配置（重要）

- 引擎 `django.db.backends.postgresql` + `psycopg`(v3)。
- 连接参数全部来自 `.env`（`settings.py` 顶部 `load_dotenv(BASE_DIR / '.env')`），字段：
  - `SUPABASE_DB_HOST` / `SUPABASE_DB_PORT` / `SUPABASE_DB_NAME` / `SUPABASE_DB_USER` / `SUPABASE_DB_PASSWORD`
- **连接方式**：使用 Supabase「会话池 Session Pooler」(端口 5432) 或直连；**切勿使用事务池 (端口 6543)**——Django 需要真实事务/会话级特性。
- **切勿把真实 `.env` 或 `SECRET_KEY` 提交到仓库或写死进代码**。

## 已知问题 / 待办（改动前注意）

- `base.html` 页脚文案仍为「Django + SQLite」，与实际（Supabase PostgreSQL）不符，属于陈旧文案。
- `settings.py` 中邮件配置用了非标准键 `MAILERS`（而非 Django 的 `EMAIL_BACKEND`），该配置实际不生效；如需邮箱功能应改为 `EMAIL_BACKEND`。
- `SECRET_KEY` 硬编码且 `DEBUG=True`，`ALLOWED_HOSTS=['localhost','127.0.0.1','testserver']`——仅适合本地开发，不可用于生产。
- `accounts/tests.py` 为空，无任何自动化测试。
- `snake_game.py` 是独立桌面脚本（标准库 `turtle`），与 Web 版解耦，尚未接入网页（网页侧仅能手动提交分数）。
- `PLAN.md` 记录了从 SQLite 迁移到 Supabase 的过程与开放问题（可作历史参考，非权威现状）。

## 约定

- 代码注释与用户可见文案均为中文。
- 表单控件统一加 Bootstrap `form-control` 类（见 `forms.py`）。
- 新增页面应继承 `accounts/base.html` 并提供 `title`/`content` block。
- 项目级 Agent 技能：`.agents/skills/playwright-cli`（浏览器自动化/测试，可用 `playwright-cli` CLI）。
- 提交改动前确保 `.env`、`db.sqlite3` 等敏感/生成文件不被纳入版本控制（已有 `.gitignore`）。
