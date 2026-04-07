from typing import Any, Dict, List


def _list_to_md(items: List[str]) -> str:
    if not items:
        return "- 无"
    return "\n".join([f"- {item}" for item in items])


def build_markdown_report(report: Dict[str, Any], retrieved_jobs: List[Dict[str, Any]]) -> str:
    summary = report.get("summary", "暂无摘要")
    match_analysis = report.get("match_analysis", {}) or {}
    job_recommendations = report.get("job_recommendations", []) or []
    action_plan = report.get("action_plan", []) or []

    score = match_analysis.get("score", "N/A")
    matched_skills = match_analysis.get("matched_skills", []) or []
    missing_skills = match_analysis.get("missing_skills", []) or []
    analysis = match_analysis.get("analysis", "暂无分析")
    suggestions = match_analysis.get("suggestions", []) or []

    md = []
    md.append("# AI 求职助手分析报告\n")
    md.append("## 一、整体结论\n")
    md.append(f"{summary}\n")

    md.append("## 二、匹配分析\n")
    md.append(f"- 匹配度：{score}\n")
    md.append("### 匹配技能")
    md.append(_list_to_md(matched_skills) + "\n")
    md.append("### 缺失技能")
    md.append(_list_to_md(missing_skills) + "\n")
    md.append("### 分析说明")
    md.append(f"{analysis}\n")
    md.append("### 优化建议")
    md.append(_list_to_md(suggestions) + "\n")

    md.append("## 三、推荐岗位\n")
    if job_recommendations:
        for i, rec in enumerate(job_recommendations, start=1):
            title = rec.get("title", "未命名岗位")
            company = rec.get("company", "未知公司")
            match_reason = rec.get("match_reason", "暂无")
            gap = rec.get("gap", []) or []
            suggestion = rec.get("suggestion", "暂无")

            md.append(f"### {i}. {title} / {company}\n")
            md.append(f"- 推荐原因：{match_reason}")
            md.append(f"- 能力缺口：\n{_list_to_md(gap)}")
            md.append(f"- 补足建议：{suggestion}\n")
    else:
        md.append("- 暂无推荐岗位\n")

    md.append("## 四、行动计划\n")
    md.append(_list_to_md(action_plan) + "\n")

    md.append("## 五、检索到的相似岗位\n")
    if retrieved_jobs:
        for i, job in enumerate(retrieved_jobs, start=1):
            title = job.get("title", "未命名岗位")
            company = job.get("company", "未知公司")
            score_text = job.get("score", "N/A")
            jd_text = job.get("jd_text", "")

            md.append(f"### {i}. {title} / {company}（相似度：{score_text}）\n")
            md.append(f"{jd_text}\n")
    else:
        md.append("- 暂无检索结果\n")

    return "\n".join(md)