# 特征中文名称映射
FEATURE_CN_MAP: dict[str, str] = {
    "age": "年龄",
    "job": "职业",
    "marital": "婚姻状态",
    "education": "教育水平",
    "default": "信贷违约",
    "housing": "住房贷款",
    "loan": "个人贷款",
    "contact": "联系方式",
    "month": "联系月份",
    "day_of_week": "联系星期",
    "duration": "通话时长(秒)",
    "campaign": "营销次数",
    "pdays": "距上次联系天数",
    "previous": "之前联系次数",
    "poutcome": "之前营销结果",
    "emp_var_rate": "就业变化率",
    "cons_price_index": "消费者物价指数",
    "cons_conf_index": "消费者信心指数",
    "lending_rate3m": "3月期贷款利率",
    "nr_employed": "雇员人数",
    "subscribe": "是否认购",
}

# 特征分类(用于分组展示)
FEATURE_CATEGORIES: dict[str, list[str]] = {
    "客户基本信息": ["age", "job", "marital", "education"],
    "客户财务状态": ["default", "housing", "loan"],
    "营销活动信息": [
        "contact",
        "month",
        "day_of_week",
        "duration",
        "campaign",
        "pdays",
        "previous",
        "poutcome",
    ],
    "宏观经济指标": [
        "emp_var_rate",
        "cons_price_index",
        "cons_conf_index",
        "lending_rate3m",
        "nr_employed",
    ],
}

# 分类值中文映射
VALUE_CN_MAP: dict[str, dict[str, str]] = {
    "job": {
        "admin.": "行政人员",
        "blue-collar": "蓝领",
        "entrepreneur": "企业家",
        "housemaid": "家政",
        "management": "管理层",
        "retired": "退休",
        "self-employed": "自由职业",
        "services": "服务业",
        "student": "学生",
        "technician": "技术人员",
        "unemployed": "无业",
        "unknown": "未知",
    },
    "marital": {
        "divorced": "离异",
        "married": "已婚",
        "single": "单身",
        "unknown": "未知",
    },
    "education": {
        "basic.4y": "基础教育4年",
        "basic.6y": "基础教育6年",
        "basic.9y": "基础教育9年",
        "high.school": "高中",
        "illiterate": "文盲",
        "professional.course": "职业课程",
        "university.degree": "大学学位",
        "unknown": "未知",
    },
    "default": {"yes": "是", "no": "否", "unknown": "未知"},
    "housing": {"yes": "是", "no": "否", "unknown": "未知"},
    "loan": {"yes": "是", "no": "否", "unknown": "未知"},
    "contact": {"cellular": "手机", "telephone": "固话"},
    "poutcome": {"failure": "失败", "nonexistent": "未曾联系", "success": "成功"},
    "subscribe": {"yes": "是", "no": "否"},
}


def get_feature_cn(name: str) -> str:
    """返回特征中文名,未映射时返回原名。"""
    return FEATURE_CN_MAP.get(name, name)


def get_value_cn(feature: str, value: str) -> str:
    """返回分类值的中文映射,未映射时返回原值。"""
    mapping = VALUE_CN_MAP.get(feature, {})
    return mapping.get(str(value), str(value))


def get_category_features(category: str) -> list[str]:
    """返回指定分类下的特征名列表。"""
    return FEATURE_CATEGORIES.get(category, [])
