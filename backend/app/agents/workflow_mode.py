"""
工作流模式定义 - 支持 5 种运行模式
"""

from enum import Enum


class WorkflowMode(str, Enum):
    """
    工作流运行模式
    
    支持的模式：
    - LITE_ANALYSIS: 快速分析（仅核心节点，~15秒）
    - FULL_ANALYSIS: 完整分析（所有节点，~45秒）
    - INTERVIEW_ONLY: 独立面试题生成（仅 interview_coach 节点，~8秒）
    - INTERVIEW_WITH_PREP: 面试包（interview_coach + learning_planner，~15秒）
    - PREP_ONLY: 仅准备计划（仅 learning_planner 节点，~6秒）
    """
    
    LITE_ANALYSIS = "lite_analysis"
    FULL_ANALYSIS = "full_analysis"
    INTERVIEW_ONLY = "interview_only"
    INTERVIEW_WITH_PREP = "interview_with_prep"
    PREP_ONLY = "prep_only"


# 各模式的配置
MODE_CONFIG = {
    WorkflowMode.LITE_ANALYSIS: {
        "nodes": [
            "start_parse",
            "jd_parser",
            "resume_parser",
            "rag_query_planner",
            "rag_retriever",
            "match_scorer",
            "gap_analyzer",
            "next_best_action",  # 到这里结束，不包含增强节点
        ],
        "estimated_time_s": 15,
        "estimated_tokens": 25000,
        "description": "快速分析：仅提供匹配度和能力缺口",
        "includes_enhancement": False,
    },
    
    WorkflowMode.FULL_ANALYSIS: {
        "nodes": [
            "start_parse",
            "jd_parser",
            "resume_parser",
            "rag_query_planner",
            "rag_retriever",
            "match_scorer",
            "gap_analyzer",
            "resume_optimizer",      # 增强节点
            "interview_coach",         # 增强节点
            "learning_planner",        # 增强节点
            "next_best_action",
        ],
        "estimated_time_s": 45,
        "estimated_tokens": 55000,
        "description": "完整分析：包含优化建议、面试题和准备计划",
        "includes_enhancement": True,
    },
    
    WorkflowMode.INTERVIEW_ONLY: {
        "nodes": [
            "interview_coach",  # 仅此节点
        ],
        "estimated_time_s": 8,
        "estimated_tokens": 8000,
        "description": "独立面试题：基于 JD/简历生成定制化题目",
        "includes_enhancement": False,
    },
    
    WorkflowMode.INTERVIEW_WITH_PREP: {
        "nodes": [
            "interview_coach",
            "learning_planner",  # 两节点顺序执行
        ],
        "estimated_time_s": 15,
        "estimated_tokens": 15000,
        "description": "面试包：面试题 + 准备计划一站式生成",
        "includes_enhancement": False,
    },
    
    WorkflowMode.PREP_ONLY: {
        "nodes": [
            "learning_planner",  # 仅此节点
        ],
        "estimated_time_s": 6,
        "estimated_tokens": 6000,
        "description": "仅准备计划：基于已有题目生成备考指南",
        "includes_enhancement": False,
    },
}


def get_required_nodes(mode: WorkflowMode) -> list[str]:
    """获取指定模式需要的节点列表"""
    config = MODE_CONFIG.get(mode)
    if config:
        return config["nodes"]
    return []


def get_mode_config(mode: WorkflowMode) -> dict:
    """获取指定模式的完整配置"""
    return MODE_CONFIG.get(mode, {})


def validate_mode(mode_str: str) -> WorkflowMode:
    """
    验证并转换模式字符串为枚举值
    
    Args:
        mode_str: 模式字符串
        
    Returns:
        WorkflowMode 枚举值
        
    Raises:
        ValueError: 如果模式字符串无效
    """
    try:
        return WorkflowMode(mode_str)
    except ValueError:
        valid_modes = [m.value for m in WorkflowMode]
        raise ValueError(
            f"无效的工作流模式: '{mode_str}'。"
            f"可选模式: {', '.join(valid_modes)}"
        )
