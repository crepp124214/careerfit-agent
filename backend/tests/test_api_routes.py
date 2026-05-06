"""API Routes 集成测试"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.schemas.jobs import JobCreate
from app.schemas.resumes import ResumeCreate


class TestJobRoutes:
    """测试职位相关 API 路由"""

    def test_create_job(self, client: TestClient):
        """测试创建职位"""
        response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Python Developer",
                "raw_text": "We need a Python developer with FastAPI experience."
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Python Developer"
        assert "id" in data
        assert "profile" in data

    def test_create_job_validation_error(self, client: TestClient):
        """测试创建职位时的验证错误"""
        # 标题太短
        response = client.post(
            "/api/v1/jobs",
            json={
                "title": "",
                "raw_text": "Valid raw text with enough length."
            }
        )
        assert response.status_code == 422

        # 原始文本太短
        response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Valid Title",
                "raw_text": "Too short"
            }
        )
        assert response.status_code == 422

    def test_get_job(self, client: TestClient):
        """测试获取职位"""
        # 先创建
        create_response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Data Analyst",
                "raw_text": "Looking for SQL and statistics experience."
            }
        )
        job_id = create_response.json()["id"]
        
        # 再获取
        response = client.get(f"/api/v1/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["title"] == "Data Analyst"

    def test_get_nonexistent_job(self, client: TestClient):
        """测试获取不存在的职位"""
        response = client.get("/api/v1/jobs/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "client_error"

    def test_list_jobs(self, client: TestClient):
        """测试列出职位"""
        # 创建多个职位
        for i in range(3):
            client.post(
                "/api/v1/jobs",
                json={
                    "title": f"Job {i}",
                    "raw_text": f"We need skill {i} experience."
                }
            )
        
        response = client.get("/api/v1/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_delete_job(self, client: TestClient):
        """测试删除职位"""
        # 先创建
        create_response = client.post(
            "/api/v1/jobs",
            json={
                "title": "To Delete",
                "raw_text": "This job will be deleted."
            }
        )
        job_id = create_response.json()["id"]
        
        # 删除
        response = client.delete(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        
        # 确认已删除
        get_response = client.get(f"/api/v1/jobs/{job_id}")
        assert get_response.status_code == 404


class TestResumeRoutes:
    """测试简历相关 API 路由"""

    def test_create_resume(self, client: TestClient):
        """测试创建简历"""
        response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "张三",
                "version_label": "v1",
                "raw_text": "I have experience with Python and FastAPI development."
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["candidate_name"] == "张三"
        assert "id" in data
        assert "profile" in data

    def test_create_resume_validation_error(self, client: TestClient):
        """测试创建简历时的验证错误"""
        # 候选人姓名太短
        response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "",
                "raw_text": "Valid raw text with enough length."
            }
        )
        assert response.status_code == 422

        # 原始文本太短
        response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "Valid Name",
                "raw_text": "Too short"
            }
        )
        assert response.status_code == 422

    def test_get_resume(self, client: TestClient):
        """测试获取简历"""
        # 先创建
        create_response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "李四",
                "version_label": "v2",
                "raw_text": "Experienced in SQL and data visualization with Python."
            }
        )
        resume_id = create_response.json()["id"]
        
        # 再获取
        response = client.get(f"/api/v1/resumes/{resume_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume_id
        assert data["candidate_name"] == "李四"

    def test_get_nonexistent_resume(self, client: TestClient):
        """测试获取不存在的简历"""
        response = client.get("/api/v1/resumes/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_list_resumes(self, client: TestClient):
        """测试列出简历"""
        # 创建多个简历
        for i in range(3):
            client.post(
                "/api/v1/resumes",
                json={
                    "candidate_name": f"候选人{i}",
                    "version_label": f"v{i}",
                    "raw_text": f"Experience with skill {i} and Python development."
                }
            )
        
        response = client.get("/api/v1/resumes")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_delete_resume(self, client: TestClient):
        """测试删除简历"""
        # 先创建
        create_response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "To Delete",
                "version_label": "v1",
                "raw_text": "This resume will be deleted."
            }
        )
        resume_id = create_response.json()["id"]
        
        # 删除
        response = client.delete(f"/api/v1/resumes/{resume_id}")
        assert response.status_code == 200
        
        # 确认已删除
        get_response = client.get(f"/api/v1/resumes/{resume_id}")
        assert get_response.status_code == 404


class TestAnalysisRoutes:
    """测试分析相关 API 路由"""

    def test_create_analysis(self, client: TestClient):
        """测试创建分析任务"""
        # 先创建职位和简历
        job_response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Python Developer",
                "raw_text": "We need a Python developer with FastAPI experience."
            }
        )
        job_id = job_response.json()["id"]
        
        resume_response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "Test Candidate",
                "version_label": "v1",
                "raw_text": "I have experience with Python and FastAPI development."
            }
        )
        resume_id = resume_response.json()["id"]
        
        # 创建分析任务
        response = client.post(
            "/api/v1/analysis",
            json={
                "job_id": job_id,
                "resume_id": resume_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "running"

    def test_create_analysis_invalid_job(self, client: TestClient):
        """测试使用无效职位创建分析"""
        response = client.post(
            "/api/v1/analysis",
            json={
                "job_id": 99999,
                "resume_id": 1
            }
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_get_analysis_status(self, client: TestClient):
        """测试获取分析状态"""
        # 先创建职位、简历和分析
        job_response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Test Job",
                "raw_text": "Test job description."
            }
        )
        job_id = job_response.json()["id"]
        
        resume_response = client.post(
            "/api/v1/resumes",
            json={
                "candidate_name": "Test",
                "version_label": "v1",
                "raw_text": "Test resume with enough length."
            }
        )
        resume_id = resume_response.json()["id"]
        
        analysis_response = client.post(
            "/api/v1/analysis",
            json={
                "job_id": job_id,
                "resume_id": resume_id
            }
        )
        analysis_id = analysis_response.json()["id"]
        
        # 获取状态
        response = client.get(f"/api/v1/analysis/{analysis_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "progress" in data


class TestErrorHandling:
    """测试错误处理"""

    def test_404_error_format(self, client: TestClient):
        """测试 404 错误格式"""
        response = client.get("/api/v1/jobs/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "type" in data["error"]
        assert "message" in data["error"]
        assert "status_code" in data["error"]

    def test_422_error_format(self, client: TestClient):
        """测试 422 验证错误格式"""
        response = client.post(
            "/api/v1/jobs",
            json={
                "title": "",
                "raw_text": "Too short"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "validation_error"

    def test_500_error_format(self, client: TestClient):
        """测试 500 错误格式（不暴露内部信息）"""
        # 触发一个服务器错误
        response = client.get("/api/v1/jobs/-1")  # 无效 ID
        
        # 应该返回安全的错误信息
        if response.status_code == 500:
            data = response.json()
            assert "error" in data
            # 确保不暴露内部实现细节
            assert "traceback" not in str(data)
            assert "internal" not in str(data).lower() or "internal_error" in str(data)

    def test_method_not_allowed(self, client: TestClient):
        """测试不允许的方法"""
        response = client.put("/api/v1/jobs")
        
        assert response.status_code == 405
        data = response.json()
        assert "error" in data
