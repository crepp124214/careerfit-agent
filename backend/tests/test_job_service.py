"""Job Service 单元测试"""
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.db.models import JobDescription
from app.schemas.jobs import JobCreate
from app.services.job_service import (
    SKILL_CATALOG,
    CASE_SENSITIVE_SKILLS,
    _find_evidence,
    _skill_pattern,
    create_job,
    get_job,
    list_jobs,
    parse_job_profile,
)


class TestSkillPattern:
    """测试技能正则表达式模式"""

    def test_skill_pattern_escape_special_chars(self):
        """测试特殊字符转义"""
        pattern = _skill_pattern("C++")
        assert pattern.search("I know C++ programming")
        assert not pattern.search("I know C programming")

    def test_skill_pattern_case_sensitive(self):
        """测试大小写敏感模式"""
        pattern = _skill_pattern("React")
        assert pattern.search("I use React")
        assert pattern.search("I use react")  # React 不在 CASE_SENSITIVE_SKILLS 中

    def test_skill_pattern_case_insensitive(self):
        """测试大小写不敏感模式"""
        pattern = _skill_pattern("python")
        assert pattern.search("I know Python")
        assert pattern.search("I know PYTHON")
        assert pattern.search("I know python")

    def test_skill_pattern_word_boundary(self):
        """测试单词边界"""
        pattern = _skill_pattern("SQL")
        assert pattern.search("I know SQL")
        assert not pattern.search("I know MySQL")  # 不应匹配 MySQL 中的 SQL


class TestFindEvidence:
    """测试证据查找功能"""

    def test_find_single_evidence(self):
        """测试查找单个证据"""
        text = "I have experience with Python. I also know Java."
        evidence = _find_evidence(text, "Python")
        assert len(evidence) == 1
        assert "Python" in evidence[0]

    def test_find_multiple_evidence(self):
        """测试查找多个证据"""
        text = "I use Python for data analysis. Python is my main language."
        evidence = _find_evidence(text, "Python")
        assert len(evidence) == 2

    def test_find_no_evidence(self):
        """测试无证据情况"""
        text = "I have experience with Java."
        evidence = _find_evidence(text, "Python")
        assert len(evidence) == 0

    def test_find_evidence_with_chinese(self):
        """测试中文文本中的证据查找"""
        text = "我熟练使用 Python 进行数据分析。我也用 Python 做过机器学习项目。"
        evidence = _find_evidence(text, "Python")
        assert len(evidence) == 2


class TestParseJobProfile:
    """测试职位解析功能"""

    def test_parse_basic_job(self):
        """测试基本职位解析"""
        text = "We need a Python developer with FastAPI experience."
        profile = parse_job_profile(text)

        assert profile["schema_version"] == "job-profile-v2"
        assert "skill_dimensions" in profile
        assert len(profile["skill_dimensions"]) > 0

    def test_parse_data_analysis_job(self):
        """测试数据分析职位解析"""
        text = "Looking for a data analyst with SQL and statistics experience."
        profile = parse_job_profile(text)

        assert profile["job_family"] == "data_analysis"
        skills = [d["name"] for d in profile["skill_dimensions"]]
        assert "SQL" in skills

    def test_parse_software_engineering_job(self):
        """测试软件工程职位解析"""
        text = "Hiring a Python developer with Docker and PostgreSQL."
        profile = parse_job_profile(text)

        assert profile["job_family"] == "software_engineering"
        skills = [d["name"] for d in profile["skill_dimensions"]]
        assert "Python" in skills

    def test_parse_empty_text(self):
        """测试空文本解析"""
        text = ""
        profile = parse_job_profile(text)

        assert len(profile["skill_dimensions"]) == 0
        assert profile["required_skills"] == []

    def test_skill_weights_sum_to_one(self):
        """测试技能权重总和为 1"""
        text = "We need Python, FastAPI, and PostgreSQL developers."
        profile = parse_job_profile(text)

        if profile["skill_dimensions"]:
            total_weight = sum(d["weight"] for d in profile["skill_dimensions"])
            assert abs(total_weight - 1.0) < 0.001


class TestJobService:
    """测试 Job Service 数据库操作"""

    def test_create_job(self, client):
        """测试创建职位"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        payload = JobCreate(
            title="Python Developer",
            raw_text="We need a Python developer with FastAPI experience."
        )
        
        job = create_job(db, payload)
        
        assert job.id is not None
        assert job.title == "Python Developer"
        assert job.profile is not None
        assert "skill_dimensions" in job.profile
        
        db.close()

    def test_get_job(self, client):
        """测试获取职位"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        # 先创建一个职位
        payload = JobCreate(
            title="Data Analyst",
            raw_text="Looking for SQL and statistics experience."
        )
        created_job = create_job(db, payload)
        
        # 再获取
        job = get_job(db, created_job.id)
        
        assert job is not None
        assert job.id == created_job.id
        assert job.title == "Data Analyst"
        
        db.close()

    def test_get_nonexistent_job(self, client):
        """测试获取不存在的职位"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        job = get_job(db, 99999)
        assert job is None
        
        db.close()

    def test_list_jobs(self, client):
        """测试列出职位"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        # 创建多个职位
        for i in range(3):
            payload = JobCreate(
                title=f"Job {i}",
                raw_text=f"We need skill {i} experience."
            )
            create_job(db, payload)
        
        jobs = list_jobs(db)
        
        assert len(jobs) == 3
        # 验证按创建时间倒序排列
        for i in range(len(jobs) - 1):
            assert jobs[i].created_at >= jobs[i + 1].created_at
        
        db.close()


class TestJobValidation:
    """测试 Job 数据验证"""

    def test_job_create_validation(self):
        """测试创建职位时的数据验证"""
        # 标题太短
        with pytest.raises(Exception):
            JobCreate(title="", raw_text="Valid raw text with enough length.")

        # 原始文本太短
        with pytest.raises(Exception):
            JobCreate(title="Valid Title", raw_text="Too short")

    def test_job_create_valid_data(self):
        """测试有效数据"""
        job = JobCreate(
            title="Python Developer",
            raw_text="We need a Python developer with FastAPI experience."
        )
        assert job.title == "Python Developer"
        assert len(job.raw_text) >= 20
