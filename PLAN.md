# 数据库迁移到 Supabase（Django 贪吃蛇项目）

## Context
- 项目：`/Users/uiber-liujie/Desktop/pi_agent`（Django 6.1.1 + Python 3.13.13，贪吃蛇 + 用户账户系统）
- 现状：`config/settings.py` 的 `DATABASES` 使用 SQLite（`BASE_DIR / 'db.sqlite3'`）
- 目标：改用 Supabase（托管 PostgreSQL），数据云端存储
- 当前环境：已装 `Django 6.1.1`、`python-dotenv 1.2.1`；**未装** `psycopg`/`psycopg2`；无 `requirements.txt`、无 `.env`

## Approach
- 用 Django 内置 `django.db.backends.postgresql` 引擎 + `psycopg`(v3) 驱动连接 Supabase 的 PostgreSQL
- 连接信息（HOST/PORT/NAME/USER/PASSWORD）放 `.env`，用已装的 `python-dotenv` 加载，避免硬编码
- 连接方式：推荐 Supabase **会话池（Session Pooler，端口 5432）** 或 **直连**；不要用事务池（端口 6543，Django 需要真实事务/会话级特性）
- 补充 `requirements.txt` 固化依赖

## Files to modify
- `config/settings.py` — 顶部加载 `.env`，替换 `DATABASES`
- 新增 `.env`（真实凭据，不提交）
- 新增 `.env.example`（占位模板）
- 新增 `requirements.txt`
- 新增 `.gitignore`（排除 `.env` / `db.sqlite3` / `__pycache__`，可选）

## Reuse
- `python-dotenv`（已装 1.2.1）→ `load_dotenv(BASE_DIR / '.env')`
- Django 自带 `django.db.backends.postgresql` 后端
- 现有 migrations 无需改动（Django 迁移与数据库无关，SQL 由后端按 DB 生成）

## Steps
- [ ] 1. 安装驱动：`pip install "psycopg[binary]"`，并写入 `requirements.txt`
- [ ] 2. 新建 `.env` + `.env.example`（`SUPABASE_DB_HOST/PORT/NAME/USER/PASSWORD`）
- [ ] 3. `settings.py`：顶部 `load_dotenv(BASE_DIR / '.env')`；`DATABASES` 改为 postgresql 并读取 env
- [ ] 4. `python manage.py migrate` 在 Supabase 建表
- [ ] 5.（可选）迁移现有 SQLite 数据：`dumpdata` → `loaddata`
- [ ] 6. 端到端验证

## Verification
- `python manage.py migrate` 无报错，Supabase 控制台出现 `auth_user` / `accounts_profile` 等表
- `python manage.py createsuperuser` 创建管理员成功
- `runserver` 后注册/登录/玩贪吃蛇，刷新后最高分仍在（证明读写走的是 Supabase）

## 待确认（Open Questions）
- [ ] 目标项目确认是 `Desktop/pi_agent`？
- [ ] 是否已有 Supabase 项目？连接信息（HOST/PASSWORD）如何提供？
- [ ] 现有 SQLite 数据（已注册用户 + 最高分）要迁移还是全新开始？
- [ ] 连接方式：默认会话池(5432) 还是直连？
