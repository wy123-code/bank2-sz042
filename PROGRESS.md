# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> **记录**:已完成事项、当前状态、下一步 TODO、关键决策(ADR)、踩坑记录(GOTCHAS)。
> **保持时间倒序、简洁、可接力。**

---

## 当前状态 · 对应六步流程:第⑤步 ✅ → 等待 CI 通过

- **第①步(建仓+Secrets)**: 2026-06-08 完成
- **第②步(开分支)**: `feature/1-project-scaffold` 从 main 切出
- **第③步(模块开发)**: 阶段 A/B/C 全部完成
- **第④步(本地 CI)**: 2026-06-08 通过
  - ruff format --check: 17 files already formatted ✅
  - ruff check: All checks passed ✅
  - pytest --cov --cov-fail-under=80: 52 passed, 100% coverage ✅
- **第⑤步(PR)**: PR #1 已创建 → https://github.com/wy123-code/bank2-sz042/pull/1
- **第⑥步(合并 + CD)**: 等待用户合并 PR → 触发 CD 部署

---

## TODO 状态

### 阶段 A · 项目骨架 (US-1)
- [x] A1: `.gitignore`
- [x] A2: `requirements.txt`
- [x] A3: `requirements-dev.txt`
- [x] A4: `Dockerfile`
- [x] A5: `.github/workflows/ci.yml`
- [x] A6: `.github/workflows/cd.yml`
- [x] A7: `src/app.py`
- [x] A8: `README.md`
- [x] A9: 本地 CI 自检 (ruff + pytest 全通过,覆盖率 99%)
- [ ] A10: 提交 PR,CI 全绿,合并 main

### 阶段 B · 数据分析页面 (US-2)
- [x] B1: `src/data_loader.py`
- [x] B2: `src/utils.py`
- [x] B3: `src/pages/01_数据分析.py` (5 卡片 + 7 图表)
- [x] B4: `tests/test_data_loader.py`
- [x] B5: 本地验证 (26 tests pass, 100% coverage on page)
- [x] B6: (合并到 A10 一起 PR)

### 阶段 C · 模型训练 & 在线预测 (US-3)
- [x] C1: `src/model_trainer.py` (LR+RF+XGB, seed=42, 最优 RF AUC=0.8871)
- [x] C2: `src/predictor.py` (单例 Predictor, 输入校验, 推理封装)
- [x] C3: `src/pages/02_在线预测.py` (20 特征表单, 预测结果展示)
- [x] C4: `tests/test_model_trainer.py`
- [x] C5: `tests/test_predictor.py`
- [x] C6: `tests/test_app.py` + `tests/test_pages.py`
- [x] C7: 本地 CI 全绿
- [x] C8: (合并到 A10 一起 PR)

---

## ADR（架构决策记录）

### ADR-1: 选择 Streamlit 而非 FastAPI+React
- **决策**: 使用 Streamlit 作为全栈框架
- **原因**: 快速构建数据应用,原生 plotly 集成,表单组件丰富,适合课程场景
- **代价**: 部署为单进程,无原生 `/health`,使用 `_stcore/health` 作为健康检查端点

### ADR-2: 标签编码 + 标准化 预处理策略
- **决策**: 分类特征用 LabelEncoder,数值特征用 StandardScaler
- **原因**: 简单可靠,所有模型通用;XGBoost 无需 One-Hot
- **代价**: 新类别出现时回退到类别 0

### ADR-3: Docker HEALTHCHECK 使用 Streamlit 内置端点
- **决策**: 使用 `_stcore/health` 作为健康检查,不引入额外健康检查服务
- **原因**: 保持架构简单,避免多端口管理

---

## GOTCHAS（踩坑记录）

### GOTCHA-1: Windows GBK 编码与 Emoji
- **现象**: `print` 输出含 ⭐ 等 emoji 时报 `UnicodeEncodeError: 'gbk' codec can't encode`
- **解决**: 替换为纯 ASCII 文本 `[BEST]`,所有打印信息使用英文

### GOTCHA-2: plotly Figure.update_xaxis vs update_xaxes
- **现象**: `AttributeError: 'Figure' object has no attribute 'update_xaxis'`
- **解决**: plotly 的 API 是 `update_xaxes`/`update_yaxes`(复数形式)

### GOTCHA-3: XGBoost 3.2.0 API 变化
- **现象**: `eval_metric` 参数在 3.2 版本行为变化
- **解决**: 封装 `_get_xgb_classifier()` 兼容不同版本,ImportError 时自动降级为两模型

### GOTCHA-4: 覆盖率 100% 与 `__main__` 守卫
- **现象**: `if __name__ == "__main__"` 守卫在测试中无法覆盖
- **解决**: 使用 `# pragma: no cover` 标注(标准做法);真正验证通过手动 `python -m src.model_trainer`
