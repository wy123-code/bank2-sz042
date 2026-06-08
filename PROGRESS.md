# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> **记录**:已完成事项、当前状态、下一步 TODO、关键决策(ADR)、踩坑记录(GOTCHAS)。
> **保持时间倒序、简洁、可接力。**

---

## 当前状态 · 对应六步流程:第①步 ✅ → 第②步

- **第①步已完成(2026-06-08)**:
  - Git 仓库初始化,`main` 分支含 13 个文件
  - GitHub 仓库:https://github.com/wy123-code/bank2-sz042
  - `.gitignore`(排除 data/、models/、.venv 等)、`README.md` 已就位
  - 人工已配置 Secrets(`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`)
- **第②步进行中**:即将从 `main` 切出 `feature/1-project-scaffold` 进入阶段 A 开发。

---

## 第一批 TODO

### 阶段 A · 项目骨架 (US-1)
- [x] A1: 创建 `.gitignore`(排除 data/、models/、__pycache__/、.venv 等)
- [ ] A2: 创建 `requirements.txt`(streamlit、pandas、plotly、scikit-learn、xgboost)
- [ ] A3: 创建 `requirements-dev.txt`(pytest、pytest-cov、ruff)
- [ ] A4: 创建 `Dockerfile`(Python 3.11-slim,端口 8009,`/health` 端点)
- [ ] A5: 创建 `.github/workflows/ci.yml`(ruff + pytest + coverage + docker build)
- [ ] A6: 创建 `.github/workflows/cd.yml`(SSH 部署 + 端口自愈 + 健康检查)
- [ ] A7: 创建 `src/app.py`(Streamlit 主入口 + `/health`)
- [x] A8: 创建 `README.md`
- [ ] A9: 本地 CI 自检通过(run ruff + pytest + coverage >= 80%)
- [ ] A10: 提交 PR,CI 全绿,合并 main,验证 CD

### 阶段 B · 数据分析页面 (US-2)
- [ ] B1: 创建 `src/data_loader.py`(加载 CSV、特征中文映射、基础统计)
- [ ] B2: 创建 `src/utils.py`(中文列名映射、格式化函数)
- [ ] B3: 创建 `src/pages/1_数据分析.py`(概览卡片 + 5+ 张 plotly 图表)
- [ ] B4: 编写 `tests/test_data_loader.py`
- [ ] B5: 本地验证:页面渲染正确、图表无重叠、指标卡片醒目
- [ ] B6: 提交 PR,CI 全绿,合并 main

### 阶段 C · 模型训练 & 在线预测 (US-3)
- [ ] C1: 创建 `src/model_trainer.py`(LR+RF+XGB,对比 AUC/F1,选最优,固定 seed)
- [ ] C2: 创建 `src/predictor.py`(加载模型、输入验证、推理封装)
- [ ] C3: 创建 `src/pages/2_在线预测.py`(点选表单 + 预测结果展示)
- [ ] C4: 编写 `tests/test_model_trainer.py`(验证模型保存、AUC >= 0.75)
- [ ] C5: 编写 `tests/test_predictor.py`(验证预测输入校验、输出格式)
- [ ] C6: 编写 `tests/test_app.py`(页面路由、health endpoint)
- [ ] C7: 本地 CI 自检全绿
- [ ] C8: 提交 PR,CI 全绿,合并 main,验证 CD

---

## ADR（架构决策记录）

_暂无,开发过程中产生后追加。_

---

## GOTCHAS（踩坑记录）

_暂无,开发过程中产生后追加。_
