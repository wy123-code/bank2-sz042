from pathlib import Path


def test_app_module_importable():
    """验证 app 模块可导入。"""
    import app

    assert app.st is not None


def test_pages_directory_exists():
    """验证 pages 目录存在且包含两个页面文件。"""
    pages_dir = Path(__file__).parent.parent / "src" / "pages"
    assert pages_dir.is_dir()
    page_files = list(pages_dir.glob("*.py"))
    page_names = {p.name for p in page_files if not p.name.startswith("__")}
    assert "01_数据分析.py" in page_names
    assert "02_在线预测.py" in page_names


def test_models_directory_exists():
    """验证 models 目录已创建。"""
    models_dir = Path(__file__).parent.parent / "models"
    assert models_dir.is_dir()
