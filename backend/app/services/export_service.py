from __future__ import annotations

from app.db.models import AnalysisReport, JobDescription, ResumeVersion


def generate_markdown_report(
    report: AnalysisReport,
    job: JobDescription,
    resume: ResumeVersion,
) -> str:
    lines: list[str] = []

    lines.append("# CareerFit 匹配分析报告")
    lines.append("")

    lines.append("## 基本信息")
    lines.append("")
    lines.append(f"- 岗位：{job.title}")
    lines.append(f"- 简历：{resume.candidate_name} — {resume.version_label}")
    lines.append(f"- 分析时间：{report.created_at}")
    lines.append(f"- 最终分数：**{report.final_score}/100**")
    lines.append("")

    breakdown = report.score_breakdown or {}
    lines.append("## 评分详情")
    lines.append("")
    lines.append("| 维度 | 分数 |")
    lines.append("|------|------|")
    dimension_labels = {
        "skill_score": "技能匹配",
        "project_score": "项目经验",
        "domain_score": "领域知识",
        "basic_requirement_score": "基本要求",
        "expression_score": "表达质量",
        "integrity_risk_penalty": "真实性风险扣分",
    }
    for key, label in dimension_labels.items():
        val = breakdown.get(key, 0)
        lines.append(f"| {label} | {val} |")
    lines.append("")

    evidence = report.evidence or []
    if evidence:
        lines.append("## 技能评分")
        lines.append("")
        for item in evidence:
            skill = item.get("skill", "")
            score = item.get("score", 0)
            lines.append(f"### {skill}")
            lines.append("")
            lines.append(f"- 评分：{score}/100")

            jd_ev = item.get("jd_evidence", [])
            if jd_ev:
                lines.append("- JD 证据：")
                for ev in jd_ev:
                    lines.append(f"  - {ev}")

            resume_ev = item.get("resume_evidence", [])
            if resume_ev:
                lines.append("- 简历证据：")
                for ev in resume_ev:
                    lines.append(f"  - {ev}")

            knowledge_ev = item.get("knowledge_evidence", [])
            if knowledge_ev:
                lines.append("- 知识库标准：")
                for ke in knowledge_ev:
                    if ke.get("available"):
                        lines.append(f"  - {ke.get('title', '未知文档')}")
                    else:
                        lines.append(f"  - {ke.get('reason', '知识库证据不足')}")
            lines.append("")

    strengths = report.strengths or []
    if strengths:
        lines.append("## 优势")
        lines.append("")
        for s in strengths:
            skill = s.get("skill", "")
            ev_list = s.get("resume_evidence", [])
            lines.append(f"**{skill}**")
            for ev in ev_list:
                lines.append(f"- {ev}")
            lines.append("")

    gaps = report.gaps or []
    if gaps:
        lines.append("## 缺口")
        lines.append("")
        for g in gaps:
            skill = g.get("skill", "")
            reason = g.get("reason", "")
            lines.append(f"- **{skill}**：{reason}")
        lines.append("")

    suggestions = report.resume_suggestions or []
    if suggestions:
        lines.append("## 简历优化建议")
        lines.append("")
        for s in suggestions:
            original = s.get("original", "")
            optimized = s.get("optimized", "")
            risk = s.get("risk_level", "")
            lines.append(f"- 原始：{original}")
            lines.append(f"  优化：{optimized}")
            if risk:
                lines.append(f"  风险等级：{risk}")
            lines.append("")

    questions = report.interview_questions or []
    if questions:
        lines.append("## 面试题")
        lines.append("")
        for q in questions:
            skill = q.get("skill", "")
            question = q.get("question", "")
            lines.append(f"- **{skill}**：{question}")
        lines.append("")

    learning = report.learning_plan or []
    if learning:
        lines.append("## 学习任务")
        lines.append("")
        for l in learning:
            skill = l.get("skill", "")
            task = l.get("task", "")
            lines.append(f"- **{skill}**：{task}")
        lines.append("")

    nba = report.next_best_action or {}
    if nba:
        lines.append("## 下一步建议")
        lines.append("")
        action = nba.get("action", "")
        reason = nba.get("reason", "")
        if action:
            lines.append(f"- **行动**：{action}")
        if reason:
            lines.append(f"- **原因**：{reason}")
        lines.append("")

    return "\n".join(lines)


def generate_html_report(
    report: AnalysisReport,
    job: JobDescription,
    resume: ResumeVersion,
) -> str:
    md = generate_markdown_report(report, job, resume)
    html_parts = ["<!DOCTYPE html>", "<html lang='zh-CN'>", "<head>", "<meta charset='utf-8'>"]
    html_parts.append("<style>")
    html_parts.append("body { font-family: -apple-system, 'Noto Sans SC', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #1a1a1a; }")
    html_parts.append("h1 { border-bottom: 2px solid #2563eb; padding-bottom: 8px; }")
    html_parts.append("h2 { border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; margin-top: 24px; }")
    html_parts.append("table { border-collapse: collapse; width: 100%; }")
    html_parts.append("th, td { border: 1px solid #d1d5db; padding: 8px; text-align: left; }")
    html_parts.append("th { background: #f3f4f6; }")
    html_parts.append("</style>")
    html_parts.append(f"<title>CareerFit 报告 - {job.title}</title>")
    html_parts.append("</head><body>")

    import re

    lines = md.split("\n")
    in_table = False
    for line in lines:
        if line.startswith("# "):
            html_parts.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            if in_table:
                html_parts.append("</table>")
                in_table = False
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_parts.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("| ") and "|" in line[2:]:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(set(c) <= {"-", ":"} for c in cells):
                continue
            if not in_table:
                html_parts.append("<table>")
                in_table = True
                html_parts.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead><tbody>")
            else:
                html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
        elif line.startswith("- "):
            content = line[2:]
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_parts.append(f"<li>{content}</li>")
        elif line.strip():
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            html_parts.append(f"<p>{content}</p>")

    if in_table:
        html_parts.append("</table>")

    html_parts.append("</body></html>")
    return "\n".join(html_parts)
