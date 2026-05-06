"""通用数据库操作仓库模块

提供标准化的 CRUD 操作，减少 Service 层的数据库操作重复代码。
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """基础数据库仓库类
    
    提供通用的 CRUD 操作，所有具体仓库应继承此类。
    
    Example:
        >>> class JobRepository(BaseRepository[JobDescription]):
        ...     def __init__(self):
        ...         super().__init__(JobDescription)
        ...
        >>> repo = JobRepository()
        >>> job = repo.get_by_id(db, 1)
        >>> jobs = repo.get_all(db, order_by="created_at")
    """

    def __init__(self, model_class: type[ModelType]):
        """初始化仓库
        
        Args:
            model_class: SQLAlchemy 模型类
        """
        self.model_class = model_class

    def get_by_id(self, db: Session, obj_id: int) -> ModelType | None:
        """根据 ID 获取对象
        
        Args:
            db: 数据库会话
            obj_id: 对象 ID
            
        Returns:
            对象实例或 None
        """
        return db.get(self.model_class, obj_id)

    def get_all(
        self,
        db: Session,
        *,
        order_by: str | None = None,
        descending: bool = True,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ModelType]:
        """获取所有对象
        
        Args:
            db: 数据库会话
            order_by: 排序字段名
            descending: 是否倒序
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            对象列表
        """
        query = db.query(self.model_class)
        
        if order_by:
            order_column = getattr(self.model_class, order_by)
            if descending:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return list(query.all())

    def create(self, db: Session, obj_data: dict[str, Any]) -> ModelType:
        """创建新对象
        
        Args:
            db: 数据库会话
            obj_data: 对象数据字典
            
        Returns:
            创建的对象实例
        """
        obj = self.model_class(**obj_data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(
        self,
        db: Session,
        obj_id: int,
        update_data: dict[str, Any],
    ) -> ModelType | None:
        """更新对象
        
        Args:
            db: 数据库会话
            obj_id: 对象 ID
            update_data: 更新数据字典
            
        Returns:
            更新后的对象实例，如果不存在则返回 None
        """
        obj = self.get_by_id(db, obj_id)
        if not obj:
            return None
        
        for key, value in update_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj_id: int) -> bool:
        """删除对象
        
        Args:
            db: 数据库会话
            obj_id: 对象 ID
            
        Returns:
            是否成功删除
        """
        obj = self.get_by_id(db, obj_id)
        if not obj:
            return False
        
        db.delete(obj)
        db.commit()
        return True

    def exists(self, db: Session, obj_id: int) -> bool:
        """检查对象是否存在
        
        Args:
            db: 数据库会话
            obj_id: 对象 ID
            
        Returns:
            是否存在
        """
        return self.get_by_id(db, obj_id) is not None

    def count(self, db: Session) -> int:
        """获取对象总数
        
        Args:
            db: 数据库会话
            
        Returns:
            对象数量
        """
        from sqlalchemy import func
        return db.query(func.count(self.model_class.id)).scalar() or 0


class JobRepository(BaseRepository):
    """职位描述仓库"""
    
    def __init__(self):
        from app.db.models import JobDescription
        super().__init__(JobDescription)


class ResumeRepository(BaseRepository):
    """简历仓库"""
    
    def __init__(self):
        from app.db.models import Resume
        super().__init__(Resume)


class AnalysisTaskRepository(BaseRepository):
    """分析任务仓库"""
    
    def __init__(self):
        from app.db.models import AnalysisTask
        super().__init__(AnalysisTask)
    
    def get_by_status(
        self,
        db: Session,
        status: str,
        order_by: str = "created_at",
    ) -> list:
        """根据状态获取任务列表"""
        query = db.query(self.model_class).filter(self.model_class.status == status)
        
        if order_by:
            order_column = getattr(self.model_class, order_by)
            query = query.order_by(order_column.desc())
        
        return list(query.all())


class AnalysisReportRepository(BaseRepository):
    """分析报告仓库"""
    
    def __init__(self):
        from app.db.models import AnalysisReport
        super().__init__(AnalysisReport)
    
    def get_by_task_id(self, db: Session, task_id: int) -> Any | None:
        """根据任务 ID 获取报告"""
        from app.db.models import AnalysisReport
        return (
            db.query(AnalysisReport)
            .filter(AnalysisReport.task_id == task_id)
            .first()
        )


# 全局仓库实例
job_repository = JobRepository()
resume_repository = ResumeRepository()
analysis_task_repository = AnalysisTaskRepository()
analysis_report_repository = AnalysisReportRepository()
