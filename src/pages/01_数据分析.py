import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_loader import get_basic_stats, get_feature_stats, load_train
from src.utils import FEATURE_CATEGORIES, get_feature_cn, get_value_cn

st.set_page_config(page_title="数据分析", page_icon="📊")

# ── 加载数据 ──────────────────────────────────────────────
try:
    df = load_train()
except FileNotFoundError:
    st.warning("⚠️ 未找到训练数据文件 `data/train.csv`,请先放置数据。")
    st.stop()

stats = get_basic_stats(df)

# ── 标题区 ──────────────────────────────────────────────
st.title("📊 银行营销数据分析看板")
st.caption(f"数据来源: 银行电话营销历史记录 · 共 {stats['total_records']:,} 条")

# ── 概览指标卡片 ─────────────────────────────────────────
st.markdown("### 📋 数据概览")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("📁 总记录数", f"{stats['total_records']:,}")
with c2:
    st.metric("📐 特征数量", stats["num_features"])
with c3:
    st.metric("✅ 认购人数", f"{stats['subscribe_yes']:,}")
with c4:
    st.metric("❌ 未认购人数", f"{stats['subscribe_no']:,}")
with c5:
    st.metric("📈 认购率", f"{stats['subscribe_rate']}%")

st.markdown("---")

# ── 第一行: 认购分布 + 年龄分布 ──────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 🥧 认购分布")
    sub_counts = df["subscribe"].value_counts().reset_index()
    sub_counts.columns = ["认购结果", "数量"]
    sub_counts["认购结果"] = sub_counts["认购结果"].map(
        lambda x: get_value_cn("subscribe", x)
    )
    fig_pie = px.pie(
        sub_counts,
        values="数量",
        names="认购结果",
        color="认购结果",
        color_discrete_map={"是": "#2ECC71", "否": "#E74C3C"},
        hole=0.4,
    )
    fig_pie.update_traces(textinfo="label+percent", textfont_size=14)
    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=380)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown("#### 📊 年龄分布 (按认购结果)")
    fig_hist = px.histogram(
        df,
        x="age",
        color="subscribe",
        color_discrete_map={"yes": "#2ECC71", "no": "#E74C3C"},
        nbins=40,
        opacity=0.7,
        barmode="overlay",
        labels={"age": "年龄", "subscribe": "认购结果"},
    )
    fig_hist.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=380)
    st.plotly_chart(fig_hist, use_container_width=True)

# ── 第二行: 职业分析 ─────────────────────────────────────
st.markdown("#### 👔 职业与认购关系")
job_data = (
    df.groupby("job")["subscribe"].value_counts().unstack(fill_value=0).reset_index()
)
job_data.columns = ["job", "no", "yes"] if "no" in job_data.columns else ["job", "yes"]
job_data["job_cn"] = job_data["job"].map(lambda x: get_value_cn("job", x))
job_data["total"] = job_data["yes"] + job_data.get("no", 0)
job_data["认购率"] = (job_data["yes"] / job_data["total"] * 100).round(1)
job_data = job_data.sort_values("total", ascending=True)

fig_job = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("各职业人数分布", "各职业认购率"),
    column_widths=[0.55, 0.45],
    specs=[[{"secondary_y": False}, {"secondary_y": False}]],
)

fig_job.add_trace(
    go.Bar(
        y=job_data["job_cn"],
        x=job_data["yes"],
        name="认购",
        orientation="h",
        marker_color="#2ECC71",
    ),
    row=1,
    col=1,
)
fig_job.add_trace(
    go.Bar(
        y=job_data["job_cn"],
        x=job_data.get("no", 0),
        name="未认购",
        orientation="h",
        marker_color="#E74C3C",
    ),
    row=1,
    col=1,
)

fig_job.add_trace(
    go.Bar(
        y=job_data["job_cn"],
        x=job_data["认购率"],
        name="认购率(%)",
        orientation="h",
        marker_color="#3498DB",
        text=job_data["认购率"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ),
    row=1,
    col=2,
)

fig_job.update_layout(
    barmode="stack",
    margin=dict(t=40, b=0, l=0, r=0),
    height=max(300, len(job_data) * 40),
    showlegend=False,
)
fig_job.update_xaxes(title_text="人数", row=1, col=1)
fig_job.update_xaxes(title_text="认购率 (%)", row=1, col=2)
st.plotly_chart(fig_job, use_container_width=True)

# ── 第三行: 月份趋势 + 星期分布 ──────────────────────────
col_month, col_dow = st.columns(2)

with col_month:
    st.markdown("#### 📅 联系月份与认购成功率")
    month_order = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]
    month_cn = {
        "jan": "1月",
        "feb": "2月",
        "mar": "3月",
        "apr": "4月",
        "may": "5月",
        "jun": "6月",
        "jul": "7月",
        "aug": "8月",
        "sep": "9月",
        "oct": "10月",
        "nov": "11月",
        "dec": "12月",
    }
    month_stats = (
        df.groupby("month")
        .agg(
            total=("subscribe", "count"),
            yes=("subscribe", lambda x: (x == "yes").sum()),
        )
        .reset_index()
    )
    month_stats["认购率"] = (month_stats["yes"] / month_stats["total"] * 100).round(1)
    month_stats["month_cn"] = month_stats["month"].map(month_cn)
    month_stats["sort_key"] = month_stats["month"].apply(
        lambda m: month_order.index(m) if m in month_order else 99
    )
    month_stats = month_stats.sort_values("sort_key")

    fig_month = go.Figure()
    fig_month.add_trace(
        go.Scatter(
            x=month_stats["month_cn"],
            y=month_stats["认购率"],
            mode="lines+markers",
            line=dict(color="#3498DB", width=3),
            marker=dict(size=10, color="#2980B9"),
            text=month_stats["认购率"].apply(lambda x: f"{x}%"),
            textposition="top center",
        )
    )
    fig_month.update_layout(
        yaxis_title="认购率 (%)",
        xaxis_title="",
        margin=dict(t=0, b=0, l=0, r=0),
        height=350,
    )
    st.plotly_chart(fig_month, use_container_width=True)

with col_dow:
    st.markdown("#### 📆 联系星期分布")
    dow_order = ["mon", "tue", "wed", "thu", "fri"]
    dow_cn = {"mon": "周一", "tue": "周二", "wed": "周三", "thu": "周四", "fri": "周五"}
    dow_data = df["day_of_week"].value_counts().reset_index()
    dow_data.columns = ["day_of_week", "count"]
    dow_data["星期"] = dow_data["day_of_week"].map(dow_cn)
    dow_data["sort_key"] = dow_data["day_of_week"].apply(
        lambda d: dow_order.index(d) if d in dow_order else 99
    )
    dow_data = dow_data.sort_values("sort_key")
    fig_dow = px.bar(
        dow_data,
        x="星期",
        y="count",
        color="星期",
        text="count",
        color_discrete_sequence=["#9B59B6", "#3498DB", "#2ECC71", "#F39C12", "#E74C3C"],
    )
    fig_dow.update_traces(textposition="outside")
    fig_dow.update_layout(
        yaxis_title="联系次数",
        xaxis_title="",
        margin=dict(t=0, b=0, l=0, r=0),
        height=350,
        showlegend=False,
    )
    st.plotly_chart(fig_dow, use_container_width=True)

# ── 第四行: 经济指标 ─────────────────────────────────────
st.markdown("#### 💹 宏观经济指标与认购关系")

eco_features = FEATURE_CATEGORIES.get("宏观经济指标", [])
eco_cols = st.columns(len(eco_features))

for i, feat in enumerate(eco_features):
    with eco_cols[i]:
        cn_name = get_feature_cn(feat)
        fig_box = px.box(
            df,
            x="subscribe",
            y=feat,
            color="subscribe",
            color_discrete_map={"yes": "#2ECC71", "no": "#E74C3C"},
            labels={"subscribe": "认购结果", feat: cn_name},
        )
        fig_box.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            height=320,
            showlegend=False,
            xaxis_title="",
        )
        fig_box.update_xaxes(tickvals=["yes", "no"], ticktext=["是", "否"])
        st.plotly_chart(fig_box, use_container_width=True)

# ── 第五行: 特征统计表 ───────────────────────────────────
st.markdown("---")
st.markdown("### 📋 特征明细统计")
feature_stats = get_feature_stats(df)
st.dataframe(
    feature_stats,
    use_container_width=True,
    hide_index=True,
    column_config={
        "特征": st.column_config.TextColumn("特征", width="medium"),
        "缺失率(%)": st.column_config.ProgressColumn(
            "缺失率(%)",
            format="%.2f%%",
            min_value=0,
            max_value=100,
        ),
    },
)
