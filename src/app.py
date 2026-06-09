import streamlit as st

st.set_page_config(
    page_title="银行营销认购预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🏦 银行营销认购预测")
st.sidebar.markdown("---")
st.sidebar.caption("基于历史营销数据的智能分析与预测平台")

st.title("🏦 银行营销认购预测系统")
st.markdown("---")

st.markdown(
    """
    ### 欢迎使用银行营销认购预测系统

    本系统基于银行电话营销历史数据,提供两大核心功能:

    | 功能 | 说明 |
    |---|---|
    | 📊 **数据分析** | 多维度可视化看板,洞察客户画像与认购行为 |
    | 🔮 **在线预测** | 基于机器学习模型,点选输入即可预测客户认购意向 |

    #### 快速开始

    请通过左侧导航栏选择您需要的功能页面。
    """
)
