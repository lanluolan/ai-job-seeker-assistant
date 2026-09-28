import React, { useEffect, useRef, useState } from 'react';
import { download, request } from './api.js';
import Result from './Result.jsx';

const tabs = [
  ['resume', '我的简历', '01'], ['match', '岗位匹配', '02'], ['optimize', '简历优化', '03'],
  ['interview', '模拟面试', '04'], ['assistant', '综合分析', '05'], ['history', '历史记录', '06'],
];
const actions = { match: '开始匹配', optimize: '生成优化建议', interview: '生成面试题', assistant: '生成求职报告' };
const emptyResume = { name: '', email: '', phone: '', summary: '', skills: [], education: [], projects: [], experiences: [] };
const pretty = value => JSON.stringify(value, null, 2);

function parseStructured(text) {
  let value;
  try { value = JSON.parse(text); } catch { throw new Error('结构化简历格式有误，请输入有效的 JSON。'); }
  if (!value || Array.isArray(value) || typeof value !== 'object') throw new Error('结构化简历必须是一个对象。');
  for (const key of ['skills', 'education', 'projects', 'experiences']) {
    if (value[key] !== undefined && !Array.isArray(value[key])) throw new Error(`${key} 必须是数组。`);
  }
  return value;
}

export default function App() {
  const [tab, setTab] = useState('resume');
  const [busy, setBusy] = useState('');
  const lock = useRef(false);
  const [notice, setNotice] = useState(null);
  const [resume, setResume] = useState('');
  const [structured, setStructured] = useState('');
  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  const fileInput = useRef(null);
  const [versions, setVersions] = useState([]);
  const [active, setActive] = useState(null);
  const [jd, setJd] = useState('');
  const [profile, setProfile] = useState('');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState({});
  const [history, setHistory] = useState([]);
  const [reports, setReports] = useState([]);
  const [detail, setDetail] = useState(null);

  async function run(label, task) {
    if (lock.current) return;
    lock.current = true;
    setBusy(label);
    setNotice(null);
    try { await task(); }
    catch (error) { setNotice({ error: true, text: error.message }); }
    finally { lock.current = false; setBusy(''); }
  }

  function loadResume(version) {
    setActive(version);
    setResume(version?.raw_text || '');
    setStructured(version?.structured_resume ? pretty(version.structured_resume) : '');
    setName(version?.resume_name || '');
    setFile(null);
    if (fileInput.current) fileInput.current.value = '';
  }

  async function refreshVersions(load = false) {
    const [list, current] = await Promise.all([request('/resume/version/list'), request('/resume/version/active')]);
    setVersions(list || []);
    setActive(current);
    if (load) loadResume(current);
  }

  useEffect(() => { run('加载简历', () => refreshVersions(true)); }, []);

  async function upload() {
    if (!file) throw new Error('请先选择简历文件。');
    const body = new FormData();
    body.append('file', file);
    const data = await request('/upload/resume', { body });
    setResume(data.text || '');
    setStructured('');
    setName(file.name.replace(/\.[^.]+$/, ''));
    setNotice({ text: '文件文字已提取，可以编辑后生成结构化简历。' });
  }

  async function analyze(event) {
    event.preventDefault();
    await run(actions[tab], async () => {
      const parsed = structured.trim() ? parseStructured(structured) : null;
      if (!resume.trim() && (!parsed || !Object.keys(parsed).length)) throw new Error('请先在「我的简历」中填写或上传简历。');
      const payload = { jd, resume_text: resume, structured_resume: parsed };
      if (tab === 'assistant') Object.assign(payload, { user_profile: profile, top_k: topK });
      const data = await request(tab === 'assistant' ? '/assistant/analyze' : `/${tab}/${tab}`, { body: payload });
      setResults(previous => ({ ...previous, [tab]: data }));
    });
  }

  async function refreshHistory() {
    const [analyses, comprehensive] = await Promise.all([request('/history/history'), request('/assistant/history')]);
    setHistory(analyses || []);
    setReports(comprehensive || []);
  }

  function reportView(data) {
    return <>
      <Result value={data.report} />
      {!!data.retrieved_jobs?.length && <details><summary>检索到的相似岗位</summary><Result value={data.retrieved_jobs} /></details>}
      <div className="actions">
        {data.markdown_report && <button type="button" className="secondary" disabled={!!busy} onClick={() => download(new Blob([data.markdown_report], { type: 'text/markdown;charset=utf-8' }), `求职报告-${data.analysis_id}.md`)}>下载 Markdown</button>}
        {data.analysis_id && <button type="button" className="secondary" disabled={!!busy} onClick={() => run('导出 PDF', async () => {
          const blob = await request(`/assistant/report/pdf/${encodeURIComponent(data.analysis_id)}`, { binary: true });
          download(blob, `求职报告-${data.analysis_id}.pdf`);
        })}>下载 PDF</button>}
      </div>
    </>;
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="#" onClick={event => { event.preventDefault(); setTab('resume'); }}><span className="brand-icon">↗</span><span>AI 求职助手<small>CAREER WORKSPACE</small></span></a>
      <p className="nav-label">求职工作台</p>
      <nav aria-label="主导航">{tabs.map(([id, title, number]) => <button key={id} disabled={!!busy} aria-current={tab === id ? 'page' : undefined} className={tab === id ? 'nav-item selected' : 'nav-item'} onClick={() => {
        setTab(id);
        setNotice(null);
        if (id === 'history') run('加载历史记录', refreshHistory);
      }}><span>{number}</span>{title}<span className="nav-arrow">↗</span></button>)}</nav>
      <div className="sidebar-note"><span className="status-dot" />你的下一步，从这里开始。<p>整理经历，发现机会，<br />为下一场面试做好准备。</p></div>
    </aside>
    <main>
      <header><span>工作台 / {tabs.find(([id]) => id === tab)[1]}</span><span className="version-badge">{active ? `当前简历 · V${active.version_no}` : '尚未激活简历版本'}</span></header>
      <div className="page-heading"><p className="eyebrow">BUILD YOUR NEXT CHAPTER</p><h1>{tabs.find(([id]) => id === tab)[1]}</h1><p>{tab === 'resume' ? '把你的经历整理好，让每一次机会都有更好的开始。' : tab === 'history' ? '回顾分析与建议，记录每一步成长。' : '结合你的简历与目标岗位，找到更清晰的求职方向。'}</p></div>
      {busy && <div className="notice" role="status"><span className="spinner" />{busy}中，请稍候…</div>}
      {notice && <div className={`notice ${notice.error ? 'error' : 'success'}`} role={notice.error ? 'alert' : 'status'}>{notice.text}</div>}
      <fieldset disabled={!!busy} className="workspace">
      {tab === 'resume' && <div className="resume-grid">
        <section className="card">
          <div className="section-heading"><h2>简历内容</h2><span className="pill">第一步</span></div>
          <div className="upload-box"><span className="upload-icon">↑</span><label htmlFor="resume-file">上传你的简历</label><p>支持 PDF、DOCX、TXT</p><input ref={fileInput} id="resume-file" type="file" accept=".pdf,.docx,.txt" onChange={event => setFile(event.target.files[0] || null)} /><button type="button" className="secondary" disabled={!file || !!busy} onClick={() => run('提取简历文字', upload)}>提取文件文字</button></div>
          <label>简历名称<input value={name} onChange={event => setName(event.target.value)} placeholder="例如：前端开发求职简历" /></label>
          <label>简历原文<textarea rows={12} value={resume} onChange={event => { setResume(event.target.value); setStructured(''); }} placeholder="也可以直接粘贴你的简历内容…" /></label>
          <p className="hint">修改原文后会清除旧的结构化内容，请重新生成；当前内容会用于各项分析。</p>
          <button type="button" disabled={!resume.trim() || !!busy} onClick={() => run('生成结构化简历', async () => {
            const data = await request('/resume/structure', { body: { resume_text: resume } });
            setStructured(pretty(data));
          })}>生成结构化简历 ↗</button>
        </section>
        <div className="stack">
          <section className="card"><div className="section-heading"><h2>结构化简历</h2><span className="pill">第二步</span></div>
            <p className="hint">提取姓名、技能与经历，检查后保存为新版本。</p>
            {structured ? <>
              <label>编辑简历 JSON<textarea className="code-editor" rows={15} value={structured} onChange={event => setStructured(event.target.value)} /></label>
              <details><summary>预览简历</summary>{(() => { try { return <Result value={parseStructured(structured)} />; } catch { return <p className="hint">修正 JSON 格式后即可预览。</p>; } })()}</details>
              <button type="button" onClick={() => run('保存简历版本', async () => {
                const parsed = parseStructured(structured);
                await request('/resume/version/save', { body: { resume_name: name || parsed.name || '未命名简历', resume_text: resume, structured_resume: parsed } });
                await refreshVersions();
                setNotice({ text: '已保存并激活新版本。' });
              })}>保存为新版本</button>
            </> : <div className="empty"><span>▤</span><p>从左侧生成结构化简历，<br />或创建空白简历开始填写。</p><button type="button" className="secondary" onClick={() => setStructured(pretty(emptyResume))}>创建空白简历</button></div>}
          </section>
          <section className="card"><div className="section-heading"><h2>版本管理</h2><button type="button" className="text-button" onClick={() => run('刷新版本', () => refreshVersions())}>刷新</button></div>
            <p className="hint">激活版本会替换页面中尚未保存的简历内容。</p>
            {versions.length ? <ul className="version-list">{versions.map(version => <li key={version.id}><div><strong>{version.resume_name || '未命名简历'}</strong><small>V{version.version_no} · {version.created_at?.slice(0, 10)}</small></div><button type="button" className="secondary" disabled={version.is_active || !!busy} onClick={() => run('激活版本', async () => {
              await request(`/resume/version/activate/${encodeURIComponent(version.id)}`, { method: 'POST' });
              await refreshVersions(true);
            })}>{version.is_active ? '使用中' : '激活'}</button></li>)}</ul> : <p className="hint">保存后，你的简历版本将出现在这里。</p>}
            <div className="actions"><button type="button" className="text-button" onClick={() => run('取消激活', async () => {
              await request('/resume/version/clear-active', { method: 'POST' });
              await refreshVersions();
              setNotice({ text: '已取消激活，页面中的简历草稿仍可编辑和分析。' });
            })}>取消当前激活版本</button><button type="button" className="text-button" onClick={() => { setResume(''); setStructured(''); setName(''); setFile(null); if (fileInput.current) fileInput.current.value = ''; setJd(''); setProfile(''); setResults({}); }}>清空页面输入</button></div>
          </section>
        </div>
      </div>}
      {actions[tab] && <div className="analysis-grid">
        <section className="card"><h2>目标与背景</h2><form onSubmit={analyze}>
          <p className="hint">使用「我的简历」中的当前内容。已填写 {resume.length} 字{structured ? '，包含结构化简历' : ''}。</p>
          {tab === 'assistant' && <label>你的背景<textarea required rows={4} value={profile} onChange={event => setProfile(event.target.value)} placeholder="例如：计算机专业应届生，有 React 项目经验，希望寻找前端开发岗位。" /></label>}
          <label>目标岗位描述（JD）<textarea required rows={13} value={jd} onChange={event => setJd(event.target.value)} placeholder="粘贴岗位职责、任职要求和你关注的信息…" /></label>
          {tab === 'assistant' && <label>相似岗位数量：{topK}<input type="range" min="1" max="10" value={topK} onChange={event => setTopK(Number(event.target.value))} /></label>}
          <button type="submit">{actions[tab]} ↗</button>
        </form></section>
        <section className="card result-card"><h2>分析结果</h2>{results[tab] ? tab === 'assistant' ? reportView(results[tab]) : <Result value={results[tab].result} /> : <div className="empty"><span>✧</span><p>填写目标岗位并开始分析，<br />在这里查看你的专属建议。</p></div>}</section>
      </div>}
      {tab === 'history' && <div className="analysis-grid">
        <section className="card"><div className="section-heading"><h2>分析记录</h2><button type="button" className="text-button" onClick={() => run('刷新历史记录', refreshHistory)}>刷新</button></div>
          <h3>综合报告</h3>{!reports.length && <p className="hint">暂无综合报告</p>}
          {reports.map(item => <button type="button" className="history-item" key={item.analysis_id} onClick={() => run('加载报告', async () => setDetail({ kind: 'report', data: await request(`/assistant/analysis/${encodeURIComponent(item.analysis_id)}`) }))}><strong>{item.jd?.slice(0, 55) || '求职分析'}</strong><small>{item.created_at?.replace('T', ' ').slice(0, 19)}</small></button>)}
          <h3>匹配 / 优化 / 面试</h3>{!history.length && <p className="hint">暂无分析记录</p>}
          {history.map(item => <button type="button" className="history-item" key={item.id} onClick={() => setDetail({ kind: 'analysis', data: item })}><strong>{tabs.find(([id]) => id === item.record_type)?.[1] || item.record_type} · {item.jd?.slice(0, 40)}</strong><small>{item.created_at?.replace('T', ' ').slice(0, 19)}</small></button>)}
        </section>
        <section className="card"><h2>记录详情</h2>{detail ? <><details><summary>查看当时的输入</summary><Result value={{ ...(detail.data.user_profile ? { 用户背景: detail.data.user_profile } : {}), 岗位描述: detail.data.jd, 简历: detail.data.resume }} /></details>{detail.kind === 'report' ? reportView(detail.data) : <Result value={detail.data.result} />}</> : <div className="empty"><span>◷</span><p>选择一条记录查看详情。</p></div>}</section>
      </div>}
      </fieldset>
      <footer>AI 生成的建议仅供参考，请结合真实经历核对内容。</footer>
    </main>
  </div>;
}
