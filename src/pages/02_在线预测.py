import streamlit as st

from src.predictor import PredictionError, get_predictor
from src.utils import get_feature_cn, VALUE_CN_MAP

st.set_page_config(page_title="在线预测", page_icon="🔮")

# ── 加载模型 ──────────────────────────────────────────────
try:
    predictor = get_predictor()
    model_ready = True
except PredictionError as e:
    model_ready = False
    model_error = str(e)

# ── 页面标题 ──────────────────────────────────────────────
st.title("🔮 银行营销认购在线预测")
st.caption("基于机器学习模型,输入客户特征即可预测是否会认购产品")

if not model_ready:
    st.error(f"⚠️ 模型未就绪: {model_error}")
    st.info("请先运行 `python -m src.model_trainer` 训练并保存模型。")
    st.stop()

# ── 模型信息 ──────────────────────────────────────────────
info = predictor.model_info
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("🤖 当前模型", info["model_name"])
with c2:
    st.metric("📈 AUC", f"{info['auc']:.4f}")
with c3:
    st.metric("🎯 F1", f"{info['f1']:.4f}")

st.markdown("---")

# ── 特征输入表单 ──────────────────────────────────────────
st.markdown("### 📝 客户特征输入")

# 反向映射: 中文 → 原值
_REVERSE_CN: dict[str, dict[str, str]] = {}
for feat, mapping in VALUE_CN_MAP.items():
    _REVERSE_CN[feat] = {v: k for k, v in mapping.items()}

with st.form("prediction_form"):
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**👤 基本信息**")
        age = st.number_input(
            get_feature_cn("age"),
            min_value=18,
            max_value=95,
            value=40,
            step=1,
        )
        job_cn = st.selectbox(
            get_feature_cn("job"),
            options=list(VALUE_CN_MAP["job"].values()),
        )
        marital_cn = st.selectbox(
            get_feature_cn("marital"),
            options=list(VALUE_CN_MAP["marital"].values()),
        )
        education_cn = st.selectbox(
            get_feature_cn("education"),
            options=list(VALUE_CN_MAP["education"].values()),
        )

    with col_b:
        st.markdown("**💰 财务状态**")
        default_cn = st.selectbox(
            get_feature_cn("default"),
            options=list(VALUE_CN_MAP["default"].values()),
        )
        housing_cn = st.selectbox(
            get_feature_cn("housing"),
            options=list(VALUE_CN_MAP["housing"].values()),
        )
        loan_cn = st.selectbox(
            get_feature_cn("loan"),
            options=list(VALUE_CN_MAP["loan"].values()),
        )
        contact_cn = st.selectbox(
            get_feature_cn("contact"),
            options=list(VALUE_CN_MAP["contact"].values()),
        )

    with col_c:
        st.markdown("**📞 营销信息**")
        month_cn = st.selectbox(
            get_feature_cn("month"),
            options=[
                "1月",
                "2月",
                "3月",
                "4月",
                "5月",
                "6月",
                "7月",
                "8月",
                "9月",
                "10月",
                "11月",
                "12月",
            ],
        )
        dow_cn = st.selectbox(
            get_feature_cn("day_of_week"),
            options=["周一", "周二", "周三", "周四", "周五"],
        )
        duration = st.number_input(
            get_feature_cn("duration"),
            min_value=0,
            max_value=5000,
            value=300,
            step=1,
        )
        campaign = st.number_input(
            get_feature_cn("campaign"),
            min_value=1,
            max_value=50,
            value=2,
            step=1,
        )

    col_d, col_e, col_f = st.columns(3)
    with col_d:
        pdays = st.number_input(
            get_feature_cn("pdays"),
            min_value=0,
            max_value=999,
            value=999,
            step=1,
        )
        previous = st.number_input(
            get_feature_cn("previous"),
            min_value=0,
            max_value=10,
            value=0,
            step=1,
        )
        poutcome_cn = st.selectbox(
            get_feature_cn("poutcome"),
            options=list(VALUE_CN_MAP["poutcome"].values()),
        )

    with col_e:
        st.markdown("**📊 经济指标(可选)**")
        emp_var_rate = st.slider(
            get_feature_cn("emp_var_rate"),
            min_value=-5.0,
            max_value=5.0,
            value=0.0,
            step=0.1,
        )
        cons_price_index = st.slider(
            get_feature_cn("cons_price_index"),
            min_value=85.0,
            max_value=100.0,
            value=93.0,
            step=0.01,
        )
        cons_conf_index = st.slider(
            get_feature_cn("cons_conf_index"),
            min_value=-60.0,
            max_value=-20.0,
            value=-38.0,
            step=0.1,
        )

    with col_f:
        lending_rate3m = st.slider(
            get_feature_cn("lending_rate3m"),
            min_value=0.0,
            max_value=10.0,
            value=4.0,
            step=0.01,
        )
        nr_employed = st.slider(
            get_feature_cn("nr_employed"),
            min_value=4800.0,
            max_value=5300.0,
            value=5100.0,
            step=0.1,
        )

    submitted = st.form_submit_button(
        "🚀 开始预测", type="primary", use_container_width=True
    )

# ── 月份/星期中文→英文映射 ────────────────────────────────
_MONTH_CN_TO_EN = {
    "1月": "jan",
    "2月": "feb",
    "3月": "mar",
    "4月": "apr",
    "5月": "may",
    "6月": "jun",
    "7月": "jul",
    "8月": "aug",
    "9月": "sep",
    "10月": "oct",
    "11月": "nov",
    "12月": "dec",
}
_DOW_CN_TO_EN = {
    "周一": "mon",
    "周二": "tue",
    "周三": "wed",
    "周四": "thu",
    "周五": "fri",
}

# ── 预测逻辑 ──────────────────────────────────────────────
if submitted:
    features = {
        "age": age,
        "job": _REVERSE_CN["job"].get(job_cn, job_cn),
        "marital": _REVERSE_CN["marital"].get(marital_cn, marital_cn),
        "education": _REVERSE_CN["education"].get(education_cn, education_cn),
        "default": _REVERSE_CN["default"].get(default_cn, default_cn),
        "housing": _REVERSE_CN["housing"].get(housing_cn, housing_cn),
        "loan": _REVERSE_CN["loan"].get(loan_cn, loan_cn),
        "contact": _REVERSE_CN["contact"].get(contact_cn, contact_cn),
        "month": _MONTH_CN_TO_EN.get(month_cn, month_cn),
        "day_of_week": _DOW_CN_TO_EN.get(dow_cn, dow_cn),
        "duration": duration,
        "campaign": campaign,
        "pdays": pdays,
        "previous": previous,
        "poutcome": _REVERSE_CN["poutcome"].get(poutcome_cn, poutcome_cn),
        "emp_var_rate": emp_var_rate,
        "cons_price_index": cons_price_index,
        "cons_conf_index": cons_conf_index,
        "lending_rate3m": lending_rate3m,
        "nr_employed": nr_employed,
    }

    result = predictor.predict(features)

    st.markdown("---")
    st.markdown("### 🎯 预测结果")

    if result["subscribe"] == "yes":
        st.success(
            f"### ✅ {result['subscribe_cn']}\n\n"
            f"**认购概率**: {result['probability']:.2%} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"**置信度**: {result['confidence']}%"
        )
    else:
        st.warning(
            f"### ❌ {result['subscribe_cn']}\n\n"
            f"**认购概率**: {result['probability']:.2%} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"**置信度**: {result['confidence']}%"
        )

    # 概率进度条
    st.progress(result["probability"], text=f"认购概率: {result['probability']:.2%}")

    with st.expander("📋 查看输入参数"):
        st.json(
            {
                get_feature_cn(k) if k in _REVERSE_CN else k: v
                for k, v in features.items()
            }
        )
