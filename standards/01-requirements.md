# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 课程作业 / 银行营销数据分析场景 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑必须有单元测试;模型训练可复现(固定 random_state)。
- **可部署**:部署后必须有健康检查 `/health` 端点。
- **性能**:预测接口响应 < 2s;数据分析页面首次加载 < 5s。

---

## 4. 需求清单

### US-1 项目初始化与 CI/CD 搭建 · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 项目根目录具备 `src/`、`tests/`、`requirements.txt`、`requirements-dev.txt`、`Dockerfile`、`.github/workflows/ci.yml`、`.github/workflows/cd.yml`、`.gitignore`。
- AC2: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC3: PR 触发 CI,包含 `ruff format --check .`、`ruff check .`、`pytest --cov --cov-fail-under=80`、`docker build`。
- AC4: CI 全绿后合并 main。
- AC5: 合并 main 自动触发 CD,端口固定 8009(被占用时在 8009~8019 区间自动回退),部署后健康检查 `/health` 通过。
- AC6: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- Streamlit 应用需提供 `/health` 端点用于健康检查。
- 数据文件与模型文件通过 `.gitignore` 排除。

---

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行业务分析师**,
我想要 一个精美的数据可视化页面,可以从多个维度查看营销数据分布与认购行为的关系,
以便 直观理解客户画像,发现影响认购的关键因素。

验收标准:
- AC1: Given 进入数据分析页面,When 页面加载,Then 显示页面标题、数据概览(总记录数、认购率、特征数量)。
- AC2: Given 数据分析页面,When 页面渲染完成,Then 至少包含以下可视化:
  - 认购分布饼图(Yes/No 比例)
  - 年龄分布直方图(按认购结果分色)
  - 职业与认购关系的分组柱状图
  - 联系月份与认购成功率折线图
  - 至少 2 个经济指标与认购关系的散点图或箱线图
- AC3: Given 数据概览卡片,When 用户查看,Then 指标数值清晰醒目,排版对齐。
- AC4: Given 职业柱状图,When 职业中文名称超过 6 个字,Then 图表不出现标签重叠或截断。
- AC5: Given 页面使用 plotly 图表,When 用户鼠标悬停图表,Then 显示交互式 tooltip 数据详情。

技术备注:
- 使用 Streamlit + plotly 实现;图表通过 `st.plotly_chart` 渲染。
- 特征中文映射表放在 `src/utils.py`,数据加载时统一转换。
- 页面文件:`src/pages/1_数据分析.py`。

---

### US-3 模型离线训练与在线预测系统 · 状态: Backlog

作为 **银行营销人员**,
我想要 通过点选表单输入客户特征后,系统基于已训练好的分类模型返回认购预测结果,
以便 在实际营销活动中预判客户是否会认购,从而精准投放资源。

验收标准:
- AC1: Given 训练脚本执行,When `model_trainer.py` 运行完毕,Then 至少训练 3 个候选模型(如逻辑回归、随机森林、XGBoost),输出各模型 AUC/F1,自动选出最优模型并保存到 `models/` 目录,且训练过程固定 `random_state=42` 保证可复现。
- AC2: Given 最优模型 AUC < 0.75 或 F1 < 0.60,When 训练完成,Then 在控制台打印警告,但不阻断部署(模型指标作为 CI 可选门禁)。
- AC3: Given 进入在线预测页面,When 页面加载,Then 显示点选表单,包含所有必需特征字段(年龄、职业、婚姻状态、教育水平、是否有房贷、是否有个人贷款、联系月份、联系星期、通话时长、营销次数、距上次联系天数、之前联系次数、之前营销结果等),默认值合理。
- AC4: Given 用户填写完整表单并点击"开始预测"按钮,When 模型推理完成,Then 页面显示预测结果:"预计会认购 ✅"或"预计不会认购 ❌",同时显示预测概率与置信度说明。
- AC5: Given 用户提交空表单或有非法输入,When 点击预测,Then 页面显示具体校验错误提示,不崩溃。
- AC6: Given 预测请求提交,When 系统进行推理,Then 单次预测响应时间 < 2 秒。

技术备注:
- 模型文件(`.pkl`)不进 Git;训练脚本在本地或 CI 运行后生成。
- 表单使用 Streamlit 原生 `st.selectbox`、`st.number_input` 等组件。
- 页面文件:`src/pages/2_在线预测.py`,预测逻辑封装在 `src/predictor.py`。
