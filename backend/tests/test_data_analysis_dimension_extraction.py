from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile


DATA_ANALYST_JD = """
岗位：数据分析师
要求：熟练使用 SQL 进行数据提取、清洗和多表关联分析；
熟悉 Python 进行数据处理和自动化分析；
能够使用 Tableau、Power BI 或 ECharts 完成数据可视化；
理解统计方法，能够设计 A/B 测试并评估显著性；
了解机器学习基础，能与算法团队协作完成特征分析。
"""


DATA_ANALYST_RESUME = """
使用 Python 和 pandas 清洗 20 万行运营数据，完成留存分析。
使用 SQL 编写多表关联查询和窗口函数，支持销售看板。
使用 ECharts 构建包含折线图、漏斗图和转化率指标的数据看板。
参与 A/B 测试结果分析，使用统计检验判断实验效果。
"""


def test_data_analyst_jd_extracts_multiple_dimensions():
    profile = parse_job_profile(DATA_ANALYST_JD)
    keys = {item["canonical_key"] for item in profile["skill_dimensions"]}

    assert profile["job_family"] == "data_analysis"
    assert len(profile["skill_dimensions"]) >= 5
    assert {"sql", "python", "data_visualization", "statistics", "ab_testing"} <= keys


def test_data_analyst_resume_extracts_matching_evidence():
    profile = parse_resume_profile(DATA_ANALYST_RESUME)
    evidence = profile["evidence"]

    assert "sql" in evidence
    assert "python" in evidence
    assert "data_visualization" in evidence
    assert "ab_testing" in evidence


def test_backend_terms_do_not_false_match_data_analysis_sql():
    profile = parse_job_profile("后端工程师，要求 SQLAlchemy、FastAPI、PostgreSQL。")

    assert profile.get("job_family") != "data_analysis"
    keys = {item["canonical_key"] for item in profile.get("skill_dimensions", [])}
    assert "sql" not in keys


def test_react_dashboard_does_not_imply_data_visualization_without_analysis_context():
    profile = parse_resume_profile("使用 React 开发后台 dashboard 页面，负责组件拆分和路由。")

    assert "data_visualization" not in profile["evidence"]
