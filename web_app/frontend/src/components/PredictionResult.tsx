import { ArrowRight, ArrowUpRight, Building2, Check, Clock3, GitBranch, Inbox, LoaderCircle, MailCheck, ScanText, ShieldCheck } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { categories, categoryNames, CopyButton, PriorityBadge } from './ui';
import type { TicketResult } from '../types/prediction';

export default function PredictionResult({ result, loading }: { result: TicketResult | null; loading: boolean }) {
  const title = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (result) {
      title.current?.focus({ preventScroll: true });
      if (window.innerWidth <= 1020) title.current?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    }
  }, [result]);
  const decision = result?.routing_decision;
  return <section className={`panel result-panel ${result ? 'has-result' : ''}`} aria-labelledby="result-title" aria-busy={loading}>
    <div className="panel-heading"><span className="section-icon"><GitBranch size={18} /></span><h2 id="result-title" ref={title} tabIndex={-1}>Kết quả điều hướng</h2><span className={`badge ${result ? 'badge-green' : 'badge-neutral'}`}>{loading ? 'Đang xử lý' : result ? 'Đã phân loại' : 'Chờ yêu cầu'}</span></div>
    {!result || !decision ? <div className="result-empty" role="status">
      <div className={`routing-illustration ${loading ? 'is-processing' : ''}`} aria-hidden="true"><span className="illustration-line line-one" /><span className="illustration-line line-two" /><span className="illustration-line line-three" /><span className="illustration-source">{loading ? <LoaderCircle size={24} className="animate-spin" /> : <ScanText size={25} />}</span><span className="illustration-target target-one"><Building2 size={18} /></span><span className="illustration-target target-two"><Building2 size={18} /></span><span className="illustration-target target-three"><Building2 size={18} /></span><span className="illustration-check"><Check size={12} /></span></div>
      <h3>{loading ? 'Đang tìm đúng phòng ban…' : 'Một yêu cầu. Đúng nơi xử lý.'}</h3><p>{loading ? 'Hệ thống đang phân tích nội dung và tạo thông tin điều hướng.' : 'Kết quả phân loại và phòng ban phụ trách sẽ xuất hiện tại đây sau khi bạn gửi yêu cầu.'}</p>
      <div className="routing-steps"><span><Inbox size={14} /> Tiếp nhận</span><ArrowRight size={12} /><span><ScanText size={14} /> Phân loại</span><ArrowRight size={12} /><span><Building2 size={14} /> Phân công</span></div>
    </div> : <div className="result-content">
      <div className="result-ticket-meta"><code>{result.ticket_id}</code><PriorityBadge priority={decision.priority_level} /></div>
      <div className="classification-heading"><span className="classification-icon"><Building2 size={23} /></span><div><p className="eyebrow">NHÓM ĐƯỢC XÁC ĐỊNH</p><h3>{decision.category_vi}</h3><span className="muted text-xs">{decision.category}</span></div><ArrowUpRight size={23} className="accent-color ml-auto" /></div>
      <div className="department-box"><span>PHÒNG BAN PHỤ TRÁCH</span><strong>{decision.target_department}</strong><code>{decision.dept_code}</code></div>
      <div className="result-metrics"><div><span><ShieldCheck size={14} /> Điểm tin cậy</span><strong>{decision.confidence_score.toFixed(2)}<small>%</small></strong></div><div><span><Clock3 size={14} /> SLA xử lý</span><strong>{decision.sla_hours}<small> giờ làm việc</small></strong></div></div>
      <div className="score-distribution"><div className="subsection-heading"><h3>Điểm phân loại</h3><span>3 nhóm</span></div>{categories.map(category => {
        const score = decision.all_class_probabilities[category] ?? 0;
        return <div className={`score-row ${decision.category === category ? 'selected' : ''}`} key={category}><div><span>{categoryNames[category]}</span><strong>{score.toFixed(2)}%</strong></div><div className="score-track" role="progressbar" aria-label={`Điểm ${categoryNames[category]}`} aria-valuenow={score} aria-valuemin={0} aria-valuemax={100}><span style={{ width: `${Math.max(0, Math.min(100, score))}%` }} /></div></div>;
      })}<p className="score-note">Điểm tin cậy là ước lượng của mô hình, hỗ trợ xem xét kết quả.</p></div>
      <div className="response-section"><div className="subsection-heading"><h3><MailCheck size={16} /> Phản hồi xác nhận</h3><CopyButton text={result.automated_response} /></div><div className="response-text" tabIndex={0} aria-label="Nội dung phản hồi xác nhận">{result.automated_response}</div></div>
    </div>}
    {!result && <div className="result-footnote"><ShieldCheck size={14} /><span>Kết quả dựa trên nội dung bạn cung cấp.</span></div>}
  </section>;
}
