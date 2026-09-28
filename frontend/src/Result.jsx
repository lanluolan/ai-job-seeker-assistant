import React from 'react';

const labels = {
  score: '匹配分数', matched_skills: '已具备的技能', missing_skills: '待补充的技能',
  analysis: '分析', suggestions: '建议', optimized_resume: '优化后的简历', change_log: '修改说明',
  missing_info: '待补充的信息', summary: '总结', match_analysis: '匹配分析',
  recommendations: '推荐岗位', job_recommendations: '推荐岗位', action_plan: '行动计划',
  title: '岗位', company: '公司', match_reason: '推荐理由', gap: '技能差距', suggestion: '建议',
  questions: '面试题', question: '问题', answer: '参考回答', reference_answer: '参考回答',
  answer_points: '回答要点', difficulty: '难度', category: '类型', jd_text: '职位描述',
  name: '姓名', email: '邮箱', phone: '电话', skills: '技能', education: '教育经历',
  projects: '项目经历', experiences: '工作经历', school: '学校', major: '专业',
  degree: '学历', period: '时间', tech_stack: '技术栈', description: '描述',
};

// Render API values as text, never as executable HTML from model output.
export default function Result({ value }) {
  if (value === null || value === undefined || value === '') return <span className="muted">暂无内容</span>;
  if (Array.isArray(value)) return value.length ? <ul className="result-list">{value.map((item, index) => <li key={index}><Result value={item} /></li>)}</ul> : <span className="muted">暂无内容</span>;
  if (typeof value === 'object') return <dl className="result-fields">{Object.entries(value).map(([key, item]) => <div key={key}><dt>{labels[key] || key}</dt><dd><Result value={item} /></dd></div>)}</dl>;
  return <span className="result-text">{String(value)}</span>;
}
