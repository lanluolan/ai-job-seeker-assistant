import html
import os
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)

# 注册中文字体，报告里中文能正常显示
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))


def _safe_text(text: Any) -> str:
    if text is None:
        return ""
    return html.escape(str(text)).replace("\n", "<br/>")


def _bullet_list(items: List[Any], style: ParagraphStyle):
    if not items:
        return [Paragraph("无", style)]
    flows = []
    for item in items:
        flows.append(ListItem(Paragraph(_safe_text(item), style)))
    return [ListFlowable(flows, bulletType="bullet")]


def build_pdf_report(
    report: Dict[str, Any],
    retrieved_jobs: List[Dict[str, Any]],
    output_path: str,
) -> str:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCN",
        parent=styles["Title"],
        fontName="STSong-Light",
        fontSize=20,
        leading=26,
        alignment=TA_LEFT,
        spaceAfter=12,
    )

    h1 = ParagraphStyle(
        "H1CN",
        parent=styles["Heading1"],
        fontName="STSong-Light",
        fontSize=15,
        leading=20,
        spaceBefore=10,
        spaceAfter=8,
    )

    h2 = ParagraphStyle(
        "H2CN",
        parent=styles["Heading2"],
        fontName="STSong-Light",
        fontSize=12,
        leading=16,
        spaceBefore=8,
        spaceAfter=6,
    )

    body = ParagraphStyle(
        "BodyCN",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=10.5,
        leading=15,
        spaceAfter=6,
    )

    elements = []

    summary = report.get("summary", "暂无摘要")
    match_analysis = report.get("match_analysis", {}) or {}
    job_recommendations = report.get("job_recommendations", []) or []
    action_plan = report.get("action_plan", []) or []

    score = match_analysis.get("score", "N/A")
    matched_skills = match_analysis.get("matched_skills", []) or []
    missing_skills = match_analysis.get("missing_skills", []) or []
    analysis = match_analysis.get("analysis", "暂无分析")
    suggestions = match_analysis.get("suggestions", []) or []

    elements.append(Paragraph("AI 求职助手分析报告", title_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("一、整体结论", h1))
    elements.append(Paragraph(_safe_text(summary), body))

    elements.append(Paragraph("二、匹配分析", h1))
    score_table = Table(
        [["匹配度", str(score)]],
        colWidths=[4 * cm, 11 * cm],
    )
    score_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(score_table)
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("匹配技能", h2))
    elements.extend(_bullet_list(matched_skills, body))
    elements.append(Paragraph("缺失技能", h2))
    elements.extend(_bullet_list(missing_skills, body))
    elements.append(Paragraph("分析说明", h2))
    elements.append(Paragraph(_safe_text(analysis), body))
    elements.append(Paragraph("优化建议", h2))
    elements.extend(_bullet_list(suggestions, body))

    elements.append(Paragraph("三、推荐岗位", h1))
    if job_recommendations:
        for i, rec in enumerate(job_recommendations, start=1):
            title = rec.get("title", "未命名岗位")
            company = rec.get("company", "未知公司")
            match_reason = rec.get("match_reason", "暂无")
            gap = rec.get("gap", []) or []
            suggestion = rec.get("suggestion", "暂无")

            elements.append(Paragraph(f"{i}. {title} / {company}", h2))
            elements.append(Paragraph(f"推荐原因：{_safe_text(match_reason)}", body))
            elements.append(Paragraph("能力缺口：", body))
            elements.extend(_bullet_list(gap, body))
            elements.append(Paragraph(f"补足建议：{_safe_text(suggestion)}", body))
    else:
        elements.append(Paragraph("暂无推荐岗位", body))

    elements.append(Paragraph("四、行动计划", h1))
    elements.extend(_bullet_list(action_plan, body))

    elements.append(Paragraph("五、检索到的相似岗位", h1))
    if retrieved_jobs:
        for i, job in enumerate(retrieved_jobs, start=1):
            title = job.get("title", "未命名岗位")
            company = job.get("company", "未知公司")
            score_text = job.get("score", "N/A")
            jd_text = job.get("jd_text", "")

            elements.append(Paragraph(f"{i}. {title} / {company}（相似度：{score_text}）", h2))
            elements.append(Paragraph(_safe_text(jd_text), body))
    else:
        elements.append(Paragraph("暂无检索结果", body))

    doc.build(elements)
    return output_path