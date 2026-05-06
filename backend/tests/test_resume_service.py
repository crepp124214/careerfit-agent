"""Resume Service 单元测试"""
from __future__ import annotations

import pytest

from app.schemas.resumes import ResumeCreate
from app.services.resume_service import (
    create_resume,
    get_resume,
    list_resumes,
    parse_resume_profile,
)


class TestParseResumeProfile:
    """测试简历解析功能"""

    def test_parse_basic_resume(self):
        """测试基本简历解析"""
        text = "I have experience with Python and FastAPI."
        profile = parse_resume_profile(text)

        assert profile["schema_version"] == "resume-profile-v2"
        assert "skills" in profile
        assert len(profile["skills"]) > 0

    def test_parse_resume_with_projects(self):
        """测试包含项目经验的简历解析"""
        text = """
        我使用 Python 完成了一个数据分析项目。
        构建了一个 Web 应用，使用 FastAPI 和 PostgreSQL。
        支持高并发请求处理。
        """
        profile = parse_resume_profile(text)

        assert "projects" in profile
        assert len(profile["projects"]) > 0

    def test_parse_resume_skills(self):
        """测试技能提取"""
        text = "I am proficient in Python, SQL, and Docker."
        profile = parse_resume_profile(text)

        skills = profile["skills"]
        assert "Python" in skills
        assert "SQL" in skills
        assert "Docker" in skills

    def test_parse_resume_evidence(self):
        """测试证据提取"""
        text = "I use Python for data analysis. I also use Python for machine learning."
        profile = parse_resume_profile(text)

        assert "evidence" in profile
        if "python" in profile["evidence"]:
            assert len(profile["evidence"]["python"]) == 2

    def test_parse_empty_resume(self):
        """测试空简历解析"""
        text = ""
        profile = parse_resume_profile(text)

        assert len(profile["skills"]) == 0
        assert len(profile["projects"]) == 0


class TestResumeService:
    """测试 Resume Service 数据库操作"""

    def test_create_resume(self, client):
        """测试创建简历"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        payload = ResumeCreate(
            candidate_name="张三",
            version_label="v1",
            raw_text="I have experience with Python and FastAPI development."
        )
        
        resume = create_resume(db, payload)
        
        assert resume.id is not None
        assert resume.candidate_name == "张三"
        assert resume.version_label == "v1"
        assert resume.profile is not None
        
        db.close()

    def test_get_resume(self, client):
        """测试获取简历"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        # 先创建一个简历
        payload = ResumeCreate(
            candidate_name="李四",
            version_label="v2",
            raw_text="Experienced in SQL and data visualization with Python."
        )
        created_resume = create_resume(db, payload)
        
        # 再获取
        resume = get_resume(db, created_resume.id)
        
        assert resume is not None
        assert resume.id == created_resume.id
        assert resume.candidate_name == "李四"
        
        db.close()

    def test_get_nonexistent_resume(self, client):
        """测试获取不存在的简历"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        resume = get_resume(db, 99999)
        assert resume is None
        
        db.close()

    def test_list_resumes(self, client):
        """测试列出简历"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        # 创建多个简历
        for i in range(3):
            payload = ResumeCreate(
                candidate_name=f"候选人{i}",
                version_label=f"v{i}",
                raw_text=f"Experience with skill {i} and Python development."
            )
            create_resume(db, payload)
        
        resumes = list_resumes(db)
        
        assert len(resumes) == 3
        # 验证按创建时间倒序排列
        for i in range(len(resumes) - 1):
            assert resumes[i].created_at >= resumes[i + 1].created_at
        
        db.close()

    def test_create_resume_with_chinese(self, client):
        """测试创建中文简历"""
        from app.db.session import SessionLocal
        db = SessionLocal()
        
        payload = ResumeCreate(
            candidate_name="王五",
            version_label="中文版",
            raw_text="我熟练使用 Python 进行数据分析，也用过 SQL 和 Docker。"
        )
        
        resume = create_resume(db, payload)
        
        assert resume.candidate_name == "王五"
        assert "Python" in resume.profile["skills"]
        
        db.close()


class TestResumeValidation:
    """测试 Resume 数据验证"""

    def test_resume_create_validation(self):
        """测试创建简历时的数据验证"""
        # 候选人姓名太短
        with pytest.raises(Exception):
            ResumeCreate(
                candidate_name="",
                raw_text="Valid raw text with enough length."
            )

        # 原始文本太短
        with pytest.raises(Exception):
            ResumeCreate(
                candidate_name="Valid Name",
                raw_text="Too short"
            )

    def test_resume_create_valid_data(self):
        """测试有效数据"""
        resume = ResumeCreate(
            candidate_name="Valid Name",
            version_label="v1",
            raw_text="I have extensive experience with Python and FastAPI development."
        )
        assert resume.candidate_name == "Valid Name"
        assert resume.version_label == "v1"
        assert len(resume.raw_text) >= 20

    def test_resume_default_version_label(self):
        """测试默认版本标签"""
        resume = ResumeCreate(
            candidate_name="Test",
            raw_text="Valid raw text with enough length for testing."
        )
        assert resume.version_label == "v1"
