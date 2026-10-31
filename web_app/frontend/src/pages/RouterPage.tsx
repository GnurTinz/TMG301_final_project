import { ArrowRight, ArrowUpRight, ChartNoAxesCombined, ChevronRight, Clock3, FileText, FlaskConical, History, Inbox, Layers3, LoaderCircle, Mail, RotateCcw, Send, ShieldCheck, Sparkles, Trash2 } from 'lucide-react';
import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { usePrediction } from '../hooks/usePrediction';
import { useHistory } from '../hooks/useHistory';
import { useResource } from '../hooks/useResource';
import { getSamples } from '../services/predictionApi';
import { categoryNames, ErrorNotice, number, PriorityBadge, shortModel } from '../components/ui';
import PredictionResult from '../components/PredictionResult';
import type { ModelInfo, Sample, TicketResult } from '../types/prediction';

export default function RouterPage({ model, connectionError, retryConnection }: { model: ModelInfo | null; connectionError: string | null; retryConnection: () => void }) {
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [validation, setValidation] = useState<{ message?: string; email?: string }>({});
  const [activeSample, setActiveSample] = useState<string | null>(null);
  const samples = useResource(getSamples);
  const prediction = usePrediction();
  const history = useHistory();
  const messageInput = useRef<HTMLTextAreaElement>(null);
  const emailInput = useRef<HTMLInputElement>(null);
  const form = useRef<HTMLFormElement>(null);

  function clear() {
    setMessage(''); setEmail(''); setValidation({}); setActiveSample(null); prediction.reset();
    messageInput.current?.focus();
  }
  function chooseSample(sample: Sample) {
    setMessage(sample.text); setEmail(sample.sender); setActiveSample(sample.id); setValidation({}); prediction.reset();
    messageInput.current?.focus();
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (prediction.loading) return;
    const errors: typeof validation = {};
    if (!message.trim()) errors.message = 'Vui lòng nhập nội dung yêu cầu hỗ trợ.';
    if (email.trim() && !emailInput.current?.validity.valid) errors.email = 'Vui lòng nhập địa chỉ email hợp lệ.';
    setValidation(errors);
    if (errors.message || errors.email) { (errors.message ? messageInput.current : emailInput.current)?.focus(); return; }
    const result = await prediction.submit({ message, customer_email: email });
    if (result) history.add(result);
  }
  function restore(ticket: TicketResult) {
    prediction.reset(); setMessage(ticket.customer_message); setEmail(ticket.customer_email); setValidation({}); setActiveSample(null); prediction.restore(ticket);
    document.getElementById('result-title')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return <>
    <section className="page-heading"><div><p className="eyebrow"><span className="tiny-line" /> LIVE TICKET ROUTER</p><h1>Điều hướng yêu cầu<span className="heading-dot">.</span></h1><p>Tiếp nhận thông tin. Phân loại rõ ràng. Đến đúng phòng ban.</p></div><a className="secondary-button analytics-link" href="#analytics"><ChartNoAxesCombined size={16} /> Xem phân tích <ArrowUpRight size={15} /></a></section>
    <div className="overview-strip" aria-label="Tổng quan mô hình"><div className="overview-item"><span className="overview-icon"><Layers3 size={18} /></span><div><span>Mô hình phân loại</span><strong>{model ? shortModel(model.model_name) : '—'} <span className="metric-detail">TF-IDF</span></strong></div></div><div className="overview-item"><span className="overview-icon"><ShieldCheck size={18} /></span><div><span>Accuracy trên tập test</span><strong>{model ? `${model.metrics.accuracy.toFixed(2)}%` : '—'} <span className="metric-detail">{model ? `${number(model.metrics.test_samples)} mẫu` : 'Chờ dữ liệu'}</span></strong></div></div><div className="overview-item"><span className="overview-icon"><Inbox size={18} /></span><div><span>Nhóm yêu cầu hỗ trợ</span><strong>{model ? String(model.classes.length).padStart(2, '0') : '—'} <span className="metric-detail">Phòng ban chuyên trách</span></strong></div></div></div>

    {connectionError && <div className="mb-5"><ErrorNotice message={connectionError} retry={retryConnection} /></div>}

    <div className="workspace-grid">
      <div className="input-column">
        <section className="panel input-panel" aria-labelledby="input-title"><div className="panel-heading"><span className="section-icon"><Mail size={18} /></span><h2 id="input-title">Yêu cầu mới</h2><span className="step-indicator">01 / TIẾP NHẬN</span></div>
          <form ref={form} noValidate onSubmit={submit} className="ticket-form" onKeyDown={event => { if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); form.current?.requestSubmit(); } }}>
            <div className="form-label-row"><label htmlFor="customer-email">Email khách hàng</label><span>Tùy chọn</span></div><div className={`input-with-icon ${validation.email ? 'invalid' : ''}`}><Mail size={16} /><input ref={emailInput} id="customer-email" type="email" autoComplete="email" placeholder="customer@example.com" value={email} disabled={prediction.loading} onChange={event => { setEmail(event.target.value); setValidation(v => ({ ...v, email: undefined })); prediction.reset(); }} aria-invalid={!!validation.email} aria-describedby={validation.email ? 'email-error' : undefined} /></div>{validation.email && <p id="email-error" className="field-error" role="alert">{validation.email}</p>}
            <div className="form-label-row message-label"><label htmlFor="customer-message">Nội dung yêu cầu <span className="required-dot">*</span></label>{message && <button type="button" className="text-button" onClick={clear} disabled={prediction.loading}><RotateCcw size={12} /> Xóa nội dung</button>}</div><textarea ref={messageInput} id="customer-message" placeholder={'Khách hàng đang gặp vấn đề gì?\n\nNhập nội dung email hoặc tin nhắn cần phân loại…'} value={message} disabled={prediction.loading} onChange={event => { setMessage(event.target.value); setActiveSample(null); setValidation(v => ({ ...v, message: undefined })); prediction.reset(); }} aria-invalid={!!validation.message} aria-describedby={validation.message ? 'message-error message-hint' : 'message-hint'} required rows={7} />
            <div className="textarea-meta"><span id="message-hint"><FileText size={12} /> Văn bản yêu cầu hỗ trợ</span><span>{number(message.length)} ký tự</span></div>{validation.message && <p id="message-error" className="field-error" role="alert">{validation.message}</p>}
            {prediction.error && <ErrorNotice message={prediction.error} />}
            <button type="submit" className="primary-button submit-button" disabled={prediction.loading}>{prediction.loading ? <LoaderCircle size={17} className="animate-spin" /> : <Send size={17} />}<span>{prediction.loading ? 'Đang phân loại yêu cầu…' : 'Phân loại & điều hướng'}</span>{!prediction.loading && <ArrowRight size={17} />}</button><p className="shortcut-hint">hoặc nhấn <kbd>Ctrl</kbd> + <kbd>Enter</kbd></p>
          </form>
        </section>

        <section className="sample-section" aria-labelledby="sample-title"><div className="sample-heading"><h2 id="sample-title"><FlaskConical size={15} /> Thử với tình huống mẫu</h2><span>Chọn để điền nội dung <ChevronRight size={12} /></span></div>{samples.loading ? <p className="muted text-sm" role="status">Đang tải tình huống mẫu…</p> : samples.error ? <ErrorNotice message={samples.error} retry={samples.reload} /> : <div className="sample-grid">{samples.data?.samples.map((sample, index) => <button type="button" className={`sample-button ${sample.id === activeSample ? 'selected' : ''}`} key={sample.id} onClick={() => chooseSample(sample)} disabled={prediction.loading} aria-pressed={sample.id === activeSample}><span className="sample-number">0{index + 1}</span><span>{sample.subject}</span><ArrowUpRight size={13} /></button>)}</div>}</section>
        <div className="workspace-note"><Sparkles size={16} /><div><strong>Từ nội dung đến hướng xử lý</strong><p>Hệ thống đề xuất phòng ban, mức ưu tiên và SLA phù hợp cho từng nhóm yêu cầu.</p></div></div>
      </div>
      <PredictionResult result={prediction.result} loading={prediction.loading} />
    </div>

    <section className="panel history-panel" aria-labelledby="history-title"><div className="panel-heading"><span className="section-icon"><History size={18} /></span><h2 id="history-title">Yêu cầu gần đây</h2><span className="count-badge">{history.items.length}</span>{history.items.length > 0 && <button type="button" className="text-button history-clear" onClick={history.clear} disabled={prediction.loading}><Trash2 size={14} /> Xóa lịch sử</button>}</div>{history.storageError && <ErrorNotice message={history.storageError} />}{history.items.length === 0 ? <div className="history-empty"><span className="empty-history-icon"><Clock3 size={20} /></span><div><strong>Chưa có yêu cầu nào được phân loại</strong><p>Lịch sử sẽ được lưu trong trình duyệt này sau lần phân loại đầu tiên.</p></div></div> : <div className="table-scroll"><table><thead><tr><th scope="col">Mã yêu cầu</th><th scope="col">Khách hàng</th><th scope="col">Phân loại</th><th scope="col">Ưu tiên</th><th scope="col">Điểm tin cậy</th><th scope="col">Thời gian</th><th scope="col"><span className="sr-only">Xem lại</span></th></tr></thead><tbody>{history.items.map(ticket => <tr key={ticket.ticket_id}><td><button type="button" className="ticket-history-link" onClick={() => restore(ticket)} disabled={prediction.loading}>{ticket.ticket_id}</button></td><td>{ticket.customer_email}</td><td><span className="badge badge-green">{categoryNames[ticket.routing_decision.category]}</span></td><td><PriorityBadge priority={ticket.routing_decision.priority_level} /></td><td className="tabular-nums font-semibold">{ticket.routing_decision.confidence_score.toFixed(2)}%</td><td className="muted">{new Date(ticket.timestamp).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' })}</td><td><button type="button" className="icon-button" onClick={() => restore(ticket)} disabled={prediction.loading} aria-label={`Xem lại ${ticket.ticket_id}`}><ArrowUpRight size={16} /></button></td></tr>)}</tbody></table></div>}<div className="table-footnote"><span className="status-dot online" /> Lưu tối đa 20 yêu cầu trên thiết bị này.</div></section>
  </>;
}
