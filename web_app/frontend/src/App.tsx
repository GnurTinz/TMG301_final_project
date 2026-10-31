import { Activity, ArrowDownLeft, ArrowRight, ArrowUpRight, ChartNoAxesCombined, ChevronRight, CircleHelp, Command, GitBranch, Inbox, Layers3, Mail, PanelLeftClose, RefreshCw, Route, ShieldCheck, Sparkles } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { getHealth, getModelInfo } from './services/predictionApi';
import { useResource } from './hooks/useResource';
import { shortModel } from './components/ui';
import RouterPage from './pages/RouterPage';
import AnalyticsPage from './pages/AnalyticsPage';

type Page = 'router' | 'analytics';
const currentPage = (): Page => window.location.hash === '#analytics' ? 'analytics' : 'router';

export default function App() {
  const [page, setPage] = useState<Page>(currentPage);
  const health = useResource(getHealth);
  const model = useResource(getModelInfo);
  const help = useRef<HTMLDialogElement>(null);
  const ready = !health.error && health.data?.model_ready;
  useEffect(() => {
    const change = () => {
      setPage(currentPage());
      requestAnimationFrame(() => {
        document.getElementById('main-content')?.focus({ preventScroll: true });
        window.scrollTo(0, 0);
      });
    };
    window.addEventListener('hashchange', change);
    return () => window.removeEventListener('hashchange', change);
  }, []);
  useEffect(() => { document.title = `${page === 'router' ? 'Điều hướng yêu cầu' : 'Phân tích mô hình'} · Ticket Router`; }, [page]);
  function retryConnection() { health.reload(); model.reload(); }

  return <div className="app-shell">
    <a className="skip-link" href="#main-content" onClick={event => { event.preventDefault(); document.getElementById('main-content')?.focus(); }}>Chuyển đến nội dung chính</a>
    <aside className="sidebar" aria-label="Thanh điều hướng">
      <a className="brand" href="#router" aria-label="Ticket Router — trang điều hướng"><span className="brand-mark"><GitBranch size={23} strokeWidth={2.2} /></span><span>ticket<span className="brand-light">router</span><small>SUPPORT WORKSPACE</small></span></a>
      <div className="workspace-label"><span className="workspace-icon"><Layers3 size={15} /></span><span>TMG301 Project</span><span className="workspace-version">01</span></div>
      <p className="nav-caption">KHÔNG GIAN LÀM VIỆC</p>
      <nav className="main-nav" aria-label="Điều hướng chính">
        <a className={`nav-item ${page === 'router' ? 'active' : ''}`} href="#router" aria-current={page === 'router' ? 'page' : undefined}><Inbox size={19} /><span>Điều hướng yêu cầu</span>{page === 'router' && <span className="nav-active-dot" />}</a>
        <a className={`nav-item ${page === 'analytics' ? 'active' : ''}`} href="#analytics" aria-current={page === 'analytics' ? 'page' : undefined}><ChartNoAxesCombined size={19} /><span>Phân tích mô hình</span>{page === 'analytics' && <span className="nav-active-dot" />}</a>
      </nav>
      <div className="sidebar-bottom">
        <div className="model-card"><div className="model-card-label"><Activity size={14} /> BỘ PHÂN LOẠI</div><strong>{model.data ? shortModel(model.data.model_name) : 'Chưa có thông tin'}</strong><span>Phân loại văn bản · 3 nhóm</span><div className="model-card-status"><i className={`status-dot ${ready ? 'online' : 'offline'}`} /><span>{health.loading ? 'Đang kiểm tra…' : ready ? 'Sẵn sàng phân loại' : 'Chưa kết nối'}</span></div></div>
        <button type="button" className="sidebar-help" onClick={() => help.current?.showModal()}><CircleHelp size={17} /> Hướng dẫn sử dụng <ArrowUpRight size={15} /></button>
        <div className="sidebar-project"><span className="project-avatar">TM</span><div><strong>Support Ticket Router</strong><span>TMG301 · Checkpoint 1</span></div><PanelLeftClose size={16} className="sidebar-footer-icon" aria-hidden="true" /></div>
      </div>
    </aside>

    <div className="main-shell">
      <header className="topbar"><div className="breadcrumbs"><Layers3 size={16} /><span>Workspace</span><ChevronRight size={13} /><strong>{page === 'router' ? 'Điều hướng' : 'Phân tích'}</strong></div><div className="topbar-right"><span className="environment-label">DEMO WORKSPACE</span><button type="button" className={`connection-status ${ready ? 'connected' : ''}`} onClick={retryConnection} title="Kiểm tra lại kết nối máy chủ"><i className={`status-dot ${ready ? 'online' : 'offline'}`} />{health.loading ? 'Đang kết nối' : ready ? 'Mô hình sẵn sàng' : 'Kết nối lại'}{!ready && !health.loading && <RefreshCw size={12} />}</button></div></header>
      <main id="main-content" className="main-content" tabIndex={-1}>
        <div hidden={page !== 'router'}><RouterPage model={model.data} connectionError={health.error} retryConnection={retryConnection} /></div>
        {page === 'analytics' && <AnalyticsPage />}
        <footer className="page-footer"><span><ShieldCheck size={13} /> Support Ticket Router <span className="footer-separator">/</span> TMG301</span><span>Phân loại rõ ràng. Xử lý đúng nơi.</span></footer>
      </main>
    </div>

    <dialog ref={help} className="help-dialog" aria-labelledby="help-title" onClick={event => { if (event.target === event.currentTarget) help.current?.close(); }}><div className="dialog-header"><span className="section-icon"><CircleHelp size={20} /></span><button type="button" className="text-button" onClick={() => help.current?.close()}>Đóng <span aria-hidden="true">×</span></button></div><p className="eyebrow">BẮT ĐẦU TRONG MỘT PHÚT</p><h2 id="help-title">Từ tin nhắn đến phòng ban.</h2><p className="muted">Dùng nội dung yêu cầu hỗ trợ hoặc chọn một trong năm mẫu có sẵn để thử hệ thống.</p><ol className="guide-steps"><li><span><Mail size={18} /></span><div><strong>Nhập yêu cầu</strong><p>Nhập nội dung và email khách hàng nếu có. Các mẫu tiếng Anh giúp bạn thử nhanh.</p></div></li><li><span><Route size={18} /></span><div><strong>Phân loại và điều hướng</strong><p>Nhấn nút phân loại hoặc Ctrl + Enter để xem nhóm, phòng ban, ưu tiên và SLA.</p></div></li><li><span><ArrowDownLeft size={18} /></span><div><strong>Xem và sao chép phản hồi</strong><p>Nội dung xác nhận được tạo để bạn sử dụng. Lịch sử được lưu trong trình duyệt này.</p></div></li></ol><div className="help-tip"><Sparkles size={17} /><span>Bạn có thể xem kết quả đánh giá và các biểu đồ ở màn hình Phân tích mô hình.</span></div><button type="button" className="primary-button w-full" onClick={() => help.current?.close()}>Bắt đầu sử dụng <ArrowRight size={16} /></button><p className="shortcut-hint"><Command size={12} /> Ctrl / ⌘ + Enter để phân loại</p></dialog>
  </div>;
}
