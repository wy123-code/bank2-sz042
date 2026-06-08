# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`bank2-sz042` — 银行营销认购预测系统
- **一句话目标**:基于银行电话营销历史数据,提供交互式数据分析看板,并构建机器学习模型实现在线认购预测。
- **使用者/受益者**:银行业务分析师、营销团队;帮助理解客户特征与认购行为,辅助营销决策。
- **核心功能**:
  - **数据分析交互页面**:精美排版,多维度可视化展示客户画像、营销效果、经济指标与认购行为的关系。
  - **在线预测系统**:基于离线训练的最优模型,用户通过点选表单输入客户特征,即时返回认购预测结果。
- **输入/数据**:
  - 数据路径:`data/train.csv` (22,500 条历史营销记录,含 `subscribe` 标签)
  - 数据路径:`data/test.csv` (7,500 条新数据,无标签,仅用于预测)
  - 数据性质:公开银行营销数据集(bank marketing),非敏感
  - 数据是否进 Git:否(CSV 文件通过 `.gitignore` 排除),模型产物不进 Git

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程要求,ML 生态成熟 |
| Web/ML 框架 | Streamlit | 快速构建数据应用,原生支持图表与表单交互 |
| 表格处理/可视化 | pandas + plotly | DataFrame 处理 + 交互式美观图表 |
| ML 建模 | scikit-learn | 经典分类模型(逻辑回归/随机森林/XGBoost),成熟可靠 |
| 测试 | pytest | 课程要求,生态统一 |
| 格式/静态检查 | ruff | 课程要求,替代 flake8 + isort + black |
| 打包/运行 | Docker | 课程要求,环境一致性 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
bank2-sz042/
├── standards/                  # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md   # 本文件
│   ├── 01-requirements.md      # 活 PRD
│   ├── PROGRESS.md             # 进度与决策记录
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   ├── 06-ai-collab-protocol.md
│   └── templates/
├── data/                       # 训练与测试数据(不进 Git)
│   ├── train.csv
│   └── test.csv
├── src/                        # 源代码
│   ├── app.py                  # Streamlit 主入口
│   ├── pages/                  # Streamlit 多页面
│   │   ├── 1_数据分析.py        # 数据分析交互页面
│   │   └── 2_在线预测.py        # 在线预测页面
│   ├── data_loader.py          # 数据加载与预处理
│   ├── model_trainer.py        # 模型训练逻辑
│   ├── predictor.py            # 预测服务封装
│   └── utils.py                # 工具函数
├── tests/                      # 测试
│   ├── test_data_loader.py
│   ├── test_model_trainer.py
│   ├── test_predictor.py
│   └── test_app.py
├── models/                     # 训练好的模型文件(不进 Git)
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖
├── Dockerfile                  # 容器部署
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── .gitignore
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `>= 80%` |
| 构建 | `docker build` 成功(CI 执行,本地不强制) |
| 业务/模型指标 | 模型 AUC >= 0.75, F1 >= 0.60(OvR 多分类加权);预测接口响应 < 2s |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物不进 Git,由 `.gitignore` 排除。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 端口固定 8009;端口被占用时自动在 8009~8019 预留区间回退(CD 端口自愈)。

## 6. 部署/CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `bank2-sz042` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/bank2-sz042` | 服务器部署目录 |
| `<PORT>` | `8009` | 固定服务端口 |
| `<PORT_MAX>` | `8019` | 端口回退上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/health` | 健康检查地址 |
| `<SSH_USER>` | `root` 或 `deploy` | 部署用户 |
| `<SSH_HOST>` | `<服务器公网 IP 或域名>` | 不写敏感信息以外的密钥 |
