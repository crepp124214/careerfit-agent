import pytest
from pydantic import ValidationError

from app.llm.agent_schemas import JDParseOutput, SkillDimension


def test_skill_dimension_requires_evidence_and_valid_weight():
    item = SkillDimension(
        name="SQL",
        canonical_key="sql",
        category="data_analysis",
        weight=0.2,
        required_level="project_practice",
        jd_evidence=["熟练使用 SQL 进行数据提取和分析"],
        aliases=["SQL", "数据库查询"],
    )

    assert item.canonical_key == "sql"


def test_skill_dimension_rejects_empty_evidence():
    with pytest.raises(ValidationError):
        SkillDimension(
            name="SQL",
            canonical_key="sql",
            category="data_analysis",
            weight=0.2,
            required_level="project_practice",
            jd_evidence=[],
            aliases=["SQL"],
        )


def test_jd_parse_output_requires_multiple_dimensions_for_data_analysis_fixture():
    output = JDParseOutput(
        job_family="data_analysis",
        dimensions=[
            SkillDimension(
                name="SQL",
                canonical_key="sql",
                category="data_analysis",
                weight=0.2,
                required_level="project_practice",
                jd_evidence=["熟练使用 SQL"],
                aliases=["SQL"],
            ),
            SkillDimension(
                name="Python",
                canonical_key="python",
                category="programming",
                weight=0.2,
                required_level="project_practice",
                jd_evidence=["熟悉 Python"],
                aliases=["Python"],
            ),
        ],
        evidence_summary="岗位要求数据提取、Python 分析和实验评估。",
    )

    assert output.job_family == "data_analysis"
    assert len(output.dimensions) == 2
