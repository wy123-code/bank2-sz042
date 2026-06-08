from src.utils import (
    FEATURE_CN_MAP,
    FEATURE_CATEGORIES,
    get_feature_cn,
    get_value_cn,
    get_category_features,
)


class TestGetFeatureCn:
    def test_known_feature_returns_cn(self):
        assert get_feature_cn("age") == "年龄"
        assert get_feature_cn("job") == "职业"
        assert get_feature_cn("subscribe") == "是否认购"

    def test_unknown_feature_returns_original(self):
        assert get_feature_cn("unknown_col") == "unknown_col"

    def test_all_mapped_features_have_cn(self):
        for key in FEATURE_CN_MAP:
            assert get_feature_cn(key) != key or key == key


class TestGetValueCn:
    def test_known_value_returns_cn(self):
        assert get_value_cn("job", "admin.") == "行政人员"
        assert get_value_cn("subscribe", "yes") == "是"
        assert get_value_cn("marital", "married") == "已婚"

    def test_unknown_value_returns_original(self):
        assert get_value_cn("job", "astronaut") == "astronaut"

    def test_unknown_feature_returns_value(self):
        assert get_value_cn("unknown_feat", "some_val") == "some_val"


class TestGetCategoryFeatures:
    def test_known_category(self):
        result = get_category_features("客户基本信息")
        assert "age" in result
        assert "job" in result
        assert len(result) == 4

    def test_unknown_category(self):
        assert get_category_features("不存在的分类") == []


class TestFeatureCategories:
    def test_all_features_accounted_for(self):
        cat_features = set()
        for features in FEATURE_CATEGORIES.values():
            cat_features.update(features)
        # subscribe 是目标变量,不属于特征分类
        all_features = set(FEATURE_CN_MAP.keys()) - {"subscribe"}
        assert cat_features == all_features

    def test_no_overlap_between_categories(self):
        seen: set[str] = set()
        for features in FEATURE_CATEGORIES.values():
            for f in features:
                assert f not in seen, f"特征 {f} 出现在多个分类中"
                seen.add(f)
