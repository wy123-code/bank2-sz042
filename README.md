# bank2-sz042 — 银行营销认购预测系统

基于银行电话营销数据,提供交互式数据分析看板与机器学习在线认购预测。

## 技术栈

Python 3.11 · Streamlit · plotly · scikit-learn · XGBoost · pytest · ruff · Docker

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt -r requirements-dev.txt

# 训练模型
python src/model_trainer.py

# 启动应用
streamlit run src/app.py --server.port 8009
```

## 项目结构

```
bank2-sz042/
├── data/                  # 数据文件(不进 Git)
├── src/                   # 源代码
├── tests/                 # 测试
├── models/                # 模型文件(不进 Git)
├── standards/             # 项目规范与进度
└── .github/workflows/     # CI/CD
```
