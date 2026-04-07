import requests
import pandas as pd
import streamlit as st
import json

st.set_page_config(page_title="AI Job Assistant", page_icon="💼", layout="wide")

API_BASE = "http://127.0.0.1:8000/api/v1"


def post_json(url: str, payload: dict):
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


def get_json(url: str):
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def get_active_resume_version_api():
    try:
        resp = requests.get(f"{API_BASE}/resume/version/active", timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def save_resume_version_api(resume_name: str, raw_text: str, structured_resume: dict):
    try:
        resp = requests.post(
            f"{API_BASE}/resume/version/save",
            json={
                "resume_name": resume_name,
                "resume_text": raw_text,
                "structured_resume": structured_resume,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


def list_resume_versions_api():
    try:
        resp = requests.get(f"{API_BASE}/resume/version/list", timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


def activate_resume_version_api(version_id: str):
    try:
        resp = requests.post(f"{API_BASE}/resume/version/activate/{version_id}", timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
    
def render_structured_resume_editor():
    structured_resume = st.session_state.get("structured_resume", {})

    if not structured_resume:
        return

    st.markdown("### Structured Resume Editor")

    with st.expander("Edit Structured Resume", expanded=False):
        name = st.text_input("Name", value=structured_resume.get("name", "") or "", key="sr_name")
        email = st.text_input("Email", value=structured_resume.get("email", "") or "", key="sr_email")
        phone = st.text_input("Phone", value=structured_resume.get("phone", "") or "", key="sr_phone")
        summary = st.text_area(
            "Summary",
            value=structured_resume.get("summary", "") or "",
            height=100,
            key="sr_summary",
        )

        skills_text = st.text_area(
            "Skills (one per line)",
            value="\n".join(structured_resume.get("skills", []) or []),
            height=120,
            key="sr_skills",
        )

        education_text = st.text_area(
            "Education (JSON array)",
            value=json.dumps(structured_resume.get("education", []) or [], ensure_ascii=False, indent=2),
            height=180,
            key="sr_education",
        )

        projects_text = st.text_area(
            "Projects (JSON array)",
            value=json.dumps(structured_resume.get("projects", []) or [], ensure_ascii=False, indent=2),
            height=220,
            key="sr_projects",
        )

        experiences_text = st.text_area(
            "Work / Internship (JSON array)",
            value=json.dumps(structured_resume.get("experiences", []) or [], ensure_ascii=False, indent=2),
            height=220,
            key="sr_experiences",
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Save Structured Resume", key="save_structured_resume"):
                try:
                    education = json.loads(education_text) if education_text.strip() else []
                    projects = json.loads(projects_text) if projects_text.strip() else []
                    experiences = json.loads(experiences_text) if experiences_text.strip() else []

                    if not isinstance(education, list):
                        raise ValueError("Education must be a JSON array")
                    if not isinstance(projects, list):
                        raise ValueError("Projects must be a JSON array")
                    if not isinstance(experiences, list):
                        raise ValueError("Work / Internship must be a JSON array")

                    updated = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "summary": summary,
                        "skills": [s.strip() for s in skills_text.splitlines() if s.strip()],
                        "education": education,
                        "projects": projects,
                        "experiences": experiences,
                    }

                    st.session_state["structured_resume"] = updated

                    # Call backend to save as a new version
                    save_result = save_resume_version_api(
                        resume_name=name or "Untitled Resume",
                        raw_text=st.session_state.get("uploaded_resume_text", ""),
                        structured_resume=updated,
                    )

                    if save_result.get("success"):
                        st.success(f"Structured resume saved, version: {save_result.get('data', {}).get('version_no')}")

                        # After saving, refresh active version and versions list
                        active_result = get_active_resume_version_api()
                        if active_result.get("success"):
                            st.session_state["active_resume_version"] = active_result.get("data")

                        version_result = list_resume_versions_api()
                        if version_result.get("success"):
                            st.session_state["resume_versions"] = version_result.get("data", [])
                    else:
                        st.warning("Saved locally, but failed to save version to server")

                except Exception as e:
                    st.error(f"Save failed: {e}")

        with col2:
            if st.button("Reset to Original Structured Result", key="reset_structured_resume"):
                st.session_state["structured_resume"] = structured_resume
                st.success("Reverted to original structured result")
    
def structure_resume_text(resume_text: str):
    try:
        resp = requests.post(
            f"{API_BASE}/resume/structure",
            json={"resume_text": resume_text},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
    
def upload_resume_file(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        resp = requests.post(f"{API_BASE}/upload/resume", files=files, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}
    
def clear_active_resume_version_api():
    try:
        resp = requests.post(f"{API_BASE}/resume/version/clear-active", timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}

def render_resume_overview(structured_resume: dict):
    name = structured_resume.get("name", "-")
    email = structured_resume.get("email", "-")
    phone = structured_resume.get("phone", "-")
    skills_count = len(structured_resume.get("skills", []) or [])
    education_count = len(structured_resume.get("education", []) or [])
    projects_count = len(structured_resume.get("projects", []) or [])
    experiences_count = len(structured_resume.get("experiences", []) or [])

    st.markdown("### Resume Overview")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Name", name)
    with c2:
        render_metric_card("Email", email)
    with c3:
        render_metric_card("Phone", phone)
    with c4:
        render_metric_card("Skills Count", str(skills_count))

    c5, c6, c7 = st.columns(3)
    with c5:
        render_metric_card("Education Count", str(education_count))
    with c6:
        render_metric_card("Projects Count", str(projects_count))
    with c7:
        render_metric_card("Experiences Count", str(experiences_count))
    
def render_job_card(rec, index=None):
    title = rec.get("title", "Untitled Job")
    company = rec.get("company", "Unknown Company")
    match_reason = rec.get("match_reason", "")
    gap = rec.get("gap", []) or []
    suggestion = rec.get("suggestion", "")
    score = rec.get("score", None)

    st.markdown(
        f"""
        <div style="
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 16px 18px;
            background: linear-gradient(180deg, #FFFFFF 0%, #FAFAFA 100%);
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            margin-bottom: 12px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                <div>
                    <div style="font-size:18px; font-weight:700; color:#111827;">
                        {f'{index}. ' if index is not None else ''}{title}
                    </div>
                    <div style="font-size:13px; color:#6B7280; margin-top:4px;">
                        {company}
                    </div>
                </div>
                <div style="
                    min-width:72px;
                    text-align:center;
                    padding:6px 10px;
                    border-radius:999px;
                    background:#EEF2FF;
                    color:#4338CA;
                    font-size:12px;
                    font-weight:700;
                ">
                    {f'Match {score}' if score is not None else 'Recommended'}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if match_reason:
        st.markdown("**Recommendation Reason**")
        st.write(match_reason)

    if gap:
        render_skills_list("Skills Gap", gap)

    if suggestion:
        st.markdown("**Suggestions**")
        st.write(suggestion)


def render_skills_list(title: str, items):
    if items:
        st.markdown(f"**{title}**")
        for item in items:
            st.write(f"- {item}")

def render_metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 14px 16px;
            background: #FFFFFF;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            margin-bottom: 8px;
        ">
            <div style="font-size: 13px; color: #6B7280; margin-bottom: 6px;">{label}</div>
            <div style="font-size: 22px; font-weight: 700; color: #111827;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_section_title(title: str):
    st.markdown(f"### {title}")

st.title("AI Job Assistant")
st.caption("Enter job JD and resume to perform matching, optimization, interview simulation, history and comprehensive analysis.")

st.markdown("### Upload Resume File")
uploaded_resume = st.file_uploader("Supports txt / pdf / docx", type=["txt", "pdf", "docx"])

if uploaded_resume:
    if st.button("Parse Resume File", key="parse_resume_btn"):
        result = upload_resume_file(uploaded_resume)
        if result.get("success"):
            resume_text = result.get("data", {}).get("text", "")
            st.session_state["uploaded_resume_text"] = resume_text
            # Write parsed text into each tab's session_state (only when the corresponding field is empty to avoid overwriting user edits)
            for _k in ("match_resume", "resume2", "resume3", "assistant_resume"):
                if resume_text and not st.session_state.get(_k):
                    st.session_state[_k] = resume_text
            st.success("Resume text extracted")
            st.text_area("Parsed resume text", value=resume_text, height=250)

            # Try structuring resume after parsing
            struct_result = structure_resume_text(resume_text)
            if struct_result.get("success"):
                st.session_state["structured_resume"] = struct_result.get("data", {})
                st.success("Resume structured successfully")
            else:
                st.error(struct_result.get("message", "Structuring failed"))
        else:
            st.error(result.get("message", "Parsing failed"))

resume_default = st.session_state.get("uploaded_resume_text", "")

# If uploaded resume text exists, use it as the default for each tab's text area during render (only when corresponding session_state is empty)
if resume_default:
    for _k in ("match_resume", "resume2", "resume3", "assistant_resume"):
        if not st.session_state.get(_k):
            st.session_state[_k] = resume_default

 # Show structured resume overview before tabs (if exists)
structured_resume = st.session_state.get("structured_resume")
if structured_resume:
    with st.expander("View Structured Resume Overview", expanded=True):
        render_resume_overview(structured_resume)

        st.markdown("#### Skills")
        skills = structured_resume.get("skills", []) or []
        if skills:
            for s in skills:
                st.write(f"- {s}")
        else:
            st.info("No skills information")

        st.markdown("#### Education")
        education = structured_resume.get("education", []) or []
        if education:
            for edu in education:
                st.write(f"- {edu.get('school','')} | {edu.get('major','')} | {edu.get('degree','')} | {edu.get('period','')}")
        else:
            st.info("No education information")

        st.markdown("#### Projects")
        projects = structured_resume.get("projects", []) or []
        if projects:
            for p in projects:
                st.write(f"- {p.get('name','')}")
                if p.get("tech_stack"):
                    st.caption(", ".join(p.get("tech_stack", [])))
        else:
            st.info("No project experience")

 # Resume version management UI
with st.expander("Resume Version Management", expanded=False):
    if st.button("Refresh Version List", key="refresh_resume_versions"):
        version_result = list_resume_versions_api()
        if version_result.get("success"):
            st.session_state["resume_versions"] = version_result.get("data", [])
        else:
            st.error(version_result.get("message", "Failed to fetch"))

    if st.button("Reset Active Version", key="clear_active_version_btn"):
        result = clear_active_resume_version_api()
        if result.get("success"):
            st.session_state["active_resume_version"] = None
            st.session_state["structured_resume"] = {}
            st.session_state["uploaded_resume_text"] = ""
            st.success("Active version cleared")

            version_result = list_resume_versions_api()
            if version_result.get("success"):
                st.session_state["resume_versions"] = version_result.get("data", [])

            st.rerun()
        else:
            st.error(result.get("message", "Reset failed"))

    if st.button("Clear Page Inputs", key="clear_page_state_btn"):
        keys_to_clear = [
            "match_jd", "match_resume",
            "jd2", "resume2",
            "jd3", "resume3",
            "assistant_profile", "assistant_resume", "assistant_jd",
            "assistant_result", "assistant_inputs",
            "resume_versions", "assistant_history", "assistant_history_detail",
            "structured_resume", "uploaded_resume_text",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Page state cleared")
        st.rerun()

    versions = st.session_state.get("resume_versions", [])
    if versions:
        for v in versions:
            col1, col2, col3 = st.columns([2.2, 1, 1])
            with col1:
                st.write(f"Version {v.get('version_no')} | {v.get('resume_name', '')}")
            with col2:
                st.write("Active" if v.get("is_active") else "Historical")
            with col3:
                if st.button("Activate", key=f"activate_{v.get('id')}"):
                    act = activate_resume_version_api(v.get("id"))
                    if act.get("success"):
                        st.success("Activated")
                        active_result = get_active_resume_version_api()
                        if active_result.get("success"):
                            st.session_state["active_resume_version"] = active_result.get("data")
                        version_result = list_resume_versions_api()
                        if version_result.get("success"):
                            st.session_state["resume_versions"] = version_result.get("data", [])
                        st.rerun()
                    else:
                        st.error(act.get("message", "Activate failed"))
    else:
        st.info("No resume versions")

st.caption("Enter job JD and resume to perform matching, optimization, interview simulation, history and comprehensive analysis.")
structured_resume = st.session_state.get("structured_resume")
if structured_resume:
    st.success("Structured resume detected and can be used for matching, optimization, and analysis.")
    render_resume_overview(structured_resume)
    render_structured_resume_editor()
else:
    st.info("No structured resume yet; upload a file to auto-parse.")

if "active_resume_version" not in st.session_state:
    active_result = get_active_resume_version_api()
    if active_result.get("success") and active_result.get("data"):
        st.session_state["active_resume_version"] = active_result.get("data")
    else:
        st.session_state["active_resume_version"] = None

active_version = st.session_state.get("active_resume_version")

if active_version:
    st.success(f"Currently active resume version: V{active_version.get('version_no')}  |  {active_version.get('resume_name', '')}")
else:
    st.info("No active resume version selected. Save or activate a version to use it for analyses.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Match Analysis", "Resume Optimization", "Interview Simulation", "History", "Comprehensive Analysis"])

with tab1:
    structured_resume = st.session_state.get("structured_resume", {})
    resume_default = st.session_state.get("uploaded_resume_text", "")
    
    st.subheader("JD + Resume Matching Analysis")
    jd = st.text_area("Job JD", height=220, placeholder="Paste job description", key="match_jd")
    resume = st.text_area("Resume", height=220, placeholder="Paste your resume", key="match_resume")
    if not resume and resume_default:
        resume = resume_default

    if st.button("Start Analysis", key="match_btn"):
        if not jd or not resume:
            st.warning("Please fill in JD and resume first.")
        else:
            payload = {
                "jd": jd,
                "resume_text": resume,
                "structured_resume": structured_resume if structured_resume else None,
            }

            result = post_json(f"{API_BASE}/match/match", payload)
            if result.get("success"):
                data = result.get("data", {})
                st.success("Analysis completed")
                st.json(data)

                inner = data.get("result", {})
                if isinstance(inner, dict):
                    score = inner.get("score")
                    if score is not None:
                        st.metric("Match Score", score)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        render_skills_list("Matched Skills", inner.get("matched_skills", []))
                    with col_b:
                        render_skills_list("Missing Skills", inner.get("missing_skills", []))
                    if inner.get("analysis"):
                        st.markdown("**Analysis Notes**")
                        st.write(inner.get("analysis"))
                    if inner.get("suggestions"):
                        render_skills_list("Improvement Suggestions", inner.get("suggestions", []))
            else:
                st.error(result.get("message", "Request failed"))

with tab2:
    st.subheader("Resume Optimization")
    # Prefer structured resume when available, keep plain text as fallback
    structured_resume = st.session_state.get("structured_resume", {})
    resume_default = st.session_state.get("uploaded_resume_text", "")

    jd2 = st.text_area("Job JD (for optimization)", height=180, placeholder="Paste job description", key="jd2")
    resume2 = st.text_area("Original Resume", height=220, placeholder="Paste resume", key="resume2")

    if not resume2 and resume_default:
        resume2 = resume_default

    if st.button("Start Optimization", key="optimize_btn"):
        if not jd2 or (not resume2 and not structured_resume):
            st.warning("Please fill in JD and resume first.")
        else:
            payload = {
                "jd": jd2,
                "resume_text": resume2,
                "structured_resume": structured_resume if structured_resume else None,
            }
            result = post_json(f"{API_BASE}/optimize/optimize", payload)

            if result.get("success"):
                data = result.get("data", {})
                st.success("Optimization completed")
                st.json(data)

                inner = data.get("result", {})
                if isinstance(inner, dict):
                    optimized_resume = inner.get("optimized_resume")
                    if optimized_resume:
                        st.markdown("### Optimized Resume")
                        st.text_area(
                            "optimized_resume",
                            value=optimized_resume,
                            height=300,
                            label_visibility="collapsed",
                        )

                    if inner.get("change_log"):
                        render_skills_list("Change Log", inner.get("change_log", []))

                    if inner.get("suggestions"):
                        render_skills_list("Suggestions", inner.get("suggestions", []))

                    if inner.get("missing_info"):
                        render_skills_list("Missing Information", inner.get("missing_info", []))
            else:
                st.error(result.get("message", "Request failed"))

with tab3:
    st.subheader("Interview Simulation")
    structured_resume = st.session_state.get("structured_resume", {})
    resume_default = st.session_state.get("uploaded_resume_text", "")

    jd3 = st.text_area("Job JD (for question generation)", height=220, placeholder="Paste job description", key="jd3")
    resume3 = st.text_area("Resume (optional)", height=180, placeholder="Optional", key="resume3")
    if not resume3 and resume_default:
        resume3 = resume_default

    if st.button("Generate Interview Questions", key="interview_btn"):
        if not jd3:
            st.warning("Please fill in JD first.")
        else:
            payload = {
                "jd": jd3,
                "resume_text": resume3,
                "structured_resume": structured_resume if structured_resume else None,
            }

            result = post_json(f"{API_BASE}/interview/interview", payload)
            if result.get("success"):
                data = result.get("data", {})
                st.success("Generation completed")
                st.json(data)

                inner = data.get("result", {})
                if isinstance(inner, dict):
                    questions = inner.get("questions", [])
                    if questions:
                        st.markdown("### Interview Questions")
                        for i, q in enumerate(questions, start=1):
                            with st.expander(f"{i}. {q.get('question', 'Unnamed question')}"):
                                st.write("Type:", q.get("type", "unknown"))
                                answer_points = q.get("answer_points", [])
                                if answer_points:
                                    st.write("Reference answer points:")
                                    for p in answer_points:
                                        st.write(f"- {p}")
            else:
                st.error(result.get("message", "Request failed"))

with tab4:
    st.subheader("History")

    col_left, col_right = st.columns([1.05, 1.95], gap="large")

    with col_left:
        if st.button("Refresh History", key="history_btn"):
            result = get_json(f"{API_BASE}/assistant/history")
            if result.get("success"):
                st.session_state["assistant_history"] = result.get("data", [])
            else:
                st.error(result.get("message", "Failed to fetch"))

        history = st.session_state.get("assistant_history", [])

        if history:
            st.markdown("#### Record List")
            options = {
                f"{item.get('created_at')} | {item.get('analysis_id')}": item.get("analysis_id")
                for item in history
            }

            selected_label = st.selectbox(
                "Select a record",
                list(options.keys()),
                index=0 if options else None,
                label_visibility="collapsed",
            )

            selected_id = options.get(selected_label)

            if selected_id:
                if st.button("View Details", key="view_history_detail"):
                    detail = get_json(f"{API_BASE}/assistant/analysis/{selected_id}")
                    if detail.get("success"):
                        st.session_state["assistant_history_detail"] = detail.get("data", {})
                    else:
                        st.error(detail.get("message", "Failed to fetch details"))
        else:
            st.info("No history records.")

    with col_right:
        detail_data = st.session_state.get("assistant_history_detail")

        if detail_data:
            report = detail_data.get("report", {}) or {}
            match_analysis = report.get("match_analysis", {}) or {}
            recommendations = report.get("job_recommendations", []) or []
            action_plan = report.get("action_plan", []) or []
            retrieved_jobs = detail_data.get("retrieved_jobs", []) or []
            markdown_report = detail_data.get("markdown_report", "")

            st.markdown("#### Record Details")

            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                render_metric_card("Analysis Record ID", str(detail_data.get("analysis_id", "-")))
            with meta_col2:
                render_metric_card("Retrieved Jobs Count", str(len(retrieved_jobs)))
            with meta_col3:
                score = match_analysis.get("score", "-")
                render_metric_card("Match Score", str(score))

            st.markdown("---")

            render_section_title("User Profile")
            st.write(detail_data.get("user_profile", ""))

            render_section_title("Target Job JD")
            st.code(detail_data.get("jd", ""))

            render_section_title("Overall Conclusion")
            summary = report.get("summary", "")
            if summary:
                st.info(summary)
            else:
                st.info("No overall conclusion.")

            render_section_title("Match Analysis")
            if isinstance(match_analysis, dict) and match_analysis:
                a1, a2 = st.columns(2)
                with a1:
                    render_skills_list("Matched Skills", match_analysis.get("matched_skills", []))
                with a2:
                    render_skills_list("Missing Skills", match_analysis.get("missing_skills", []))

                if match_analysis.get("analysis"):
                    st.markdown("**Analysis Notes**")
                    st.write(match_analysis.get("analysis"))

                if match_analysis.get("suggestions"):
                    render_skills_list("Improvement Suggestions", match_analysis.get("suggestions", []))
            else:
                st.info("No match analysis available.")

            render_section_title("Recommended Jobs")
            if recommendations:
                for i, rec in enumerate(recommendations, start=1):
                    render_job_card(rec, index=i)
            else:
                st.info("No recommended jobs.")

            render_section_title("Action Plan")
            if action_plan:
                for step in action_plan:
                    st.write(f"- {step}")
            else:
                st.info("No action plan.")

            render_section_title("Retrieved Similar Jobs")
            if retrieved_jobs:
                for item in retrieved_jobs:
                    with st.expander(
                        f"{item.get('title', '')} / {item.get('company', '')} | Similarity {item.get('score', '')}",
                        expanded=False,
                    ):
                        st.write(item.get("jd_text", ""))
            else:
                st.info("No retrieved jobs.")

            render_section_title("Export Report")
            if markdown_report:
                st.download_button(
                    label="Download Markdown Report",
                    data=markdown_report,
                    file_name=f"ai_job_assistant_{detail_data.get('analysis_id')}.md",
                    mime="text/markdown",
                    key="history_md_download",
                )

            if st.button("Download PDF Report", key="history_pdf_btn"):
                try:
                    pdf_resp = requests.get(
                        f"{API_BASE}/assistant/report/pdf/{detail_data.get('analysis_id')}",
                        timeout=180,
                    )
                    pdf_resp.raise_for_status()
                    st.download_button(
                        label="Save PDF File",
                        data=pdf_resp.content,
                        file_name=f"ai_job_assistant_{detail_data.get('analysis_id')}.pdf",
                        mime="application/pdf",
                        key="history_pdf_save",
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
        else:
            st.info("Select a history record on the left, then click 'View Details'.")

with tab5:
    st.subheader("Comprehensive Job Analysis")

    user_profile = st.text_area(
        "Your background",
        height=140,
        placeholder="e.g.: Master's student, know Python, built a recommender-system project, seeking AI application engineer role",
        key="assistant_profile",
    )
    assistant_resume = st.text_area(
        "Resume",
        height=180,
        placeholder="Paste your resume",
        key="assistant_resume",
    )
    assistant_jd = st.text_area(
        "Target Job JD",
        height=180,
        placeholder="Paste target job description",
        key="assistant_jd",
    )
    top_k = st.slider("Number of similar jobs to retrieve", 1, 10, 5, key="assistant_topk")

    structured_resume = st.session_state.get("structured_resume", {})
    resume_default = st.session_state.get("uploaded_resume_text", "")

    if not assistant_resume and resume_default:
        assistant_resume = resume_default

    if st.button("Start Comprehensive Analysis", key="assistant_btn"):
        if not user_profile or not assistant_jd:
            st.warning("Please fill in your background and target JD first.")
        else:
            payload = {
                "user_profile": user_profile,
                "resume_text": "",
                "structured_resume": None,
                "jd": assistant_jd,
                "top_k": top_k,
            }

            result = post_json(f"{API_BASE}/assistant/analyze", payload)

            if result.get("success"):
                st.session_state["assistant_result"] = result.get("data", {})
                st.session_state["assistant_inputs"] = {
                    "user_profile": user_profile,
                    "resume_text": assistant_resume,
                    "structured_resume": structured_resume,
                    "jd": assistant_jd,
                    "top_k": top_k,
                }
                st.success("Analysis completed")
            else:
                st.error(result.get("message", "Request failed"))