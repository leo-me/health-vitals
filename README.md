## file architecture

```
health-data-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # 应用入口
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── api.py          # 路由汇总
│   │   │   │   └── endpoints/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── health.py   # 健康数据 API
│   │   │   │       ├── users.py    # 用户 API
│   │   │   │       ├── alerts.py   # 告警 API
│   │   │   │       └── analytics.py # 分析 API
│   │   │   └── deps.py             # 依赖注入
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # 基础 CRUD
│   │   │   ├── crud_user.py
│   │   │   ├── crud_health_data.py
│   │   │   └── crud_alert.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py             # User ORM 模型
│   │   │   ├── health.py           # HealthData ORM 模型
│   │   │   └── alert.py            # Alert ORM 模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User Pydantic 模型
│   │   │   ├── health.py           # HealthData Pydantic 模型
│   │   │   └── alert.py            # Alert Pydantic 模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── health_service.py   # 健康数据处理逻辑
│   │   │   ├── alert_service.py    # 告警规则逻辑
│   │   │   └── s3_service.py       # AWS S3 文件上传
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── security.py         # JWT + 密码处理
│   │   │   ├── constants.py        # 常量
│   │   │   └── exceptions.py       # 自定义异常
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base 类
│   │   │   ├── session.py          # 数据库连接
│   │   │   └── init_db.py          # 初始化数据库
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py          # 日志中间件
│   │   │   └── cors.py             # CORS 配置
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py           # 日志工具
│   │       └── validators.py       # 数据验证工具
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py             # Pytest 配置
│   │   ├── test_api.py
│   │   └── test_services.py
│   ├── migrations/                 # Alembic 数据库迁移
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/
│   ├── .env.example                # 环境变量示例
│   ├── requirements.txt            # Python 依赖
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pytest.ini
│   ├── .gitignore
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DataTable.jsx
│   │   │   ├── ChartWidget.jsx
│   │   │   └── UserMenu.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── useHealthData.js
│   │   ├── services/
│   │   │   └── api.js              # Axios 实例
│   │   ├── store/
│   │   │   └── store.js            # Zustand store
│   │   ├── styles/
│   │   │   └── tailwind.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── README.md
│
├── infra/
│   ├── docker-compose.yml          # 本地开发环境
│   ├── docker-compose.prod.yml     # 生产环境
│   ├── aws/
│   │   ├── terraform/              # IaC 配置（可选）
│   │   └── README.md
│   └── README.md
│
├── docs/
│   ├── ARCHITECTURE.md             # 架构设计文档
│   ├── API.md                      # API 文档
│   ├── DEPLOYMENT.md               # 部署指南
│   ├── DATABASE.md                 # 数据库设计
│   └── CONTRIBUTING.md             # 贡献指南
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml          # 后端 CI/CD
│       └── frontend-ci.yml         # 前端 CI/CD
│
├── .gitignore
├── README.md                       # 项目总述
└── LICENSE
```

