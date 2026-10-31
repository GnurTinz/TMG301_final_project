import { AlertCircle, Check, Copy, LoaderCircle, RefreshCw } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import type { Category, Priority } from '../types/prediction';

export const categories: Category[] = ['Technical Issue', 'Payment', 'Return/Refund'];
export const categoryNames: Record<Category, string> = { 'Technical Issue': 'Lỗi kỹ thuật', Payment: 'Thanh toán', 'Return/Refund': 'Đổi trả / Hoàn tiền' };
export const number = (value: number) => new Intl.NumberFormat('vi-VN').format(value);
export const percent = (value: number) => `${(value * 100).toFixed(2)}%`;
export const shortModel = (name: string) => name.match(/\(([^)]+)\)/)?.[1] === 'Baseline' ? 'Logistic Regression' : name.match(/\(([^)]+)\)/)?.[1] || name;

export function ErrorNotice({ message, retry }: { message: string; retry?: () => void }) {
  return <div className="error-notice" role="alert"><AlertCircle size={18} className="shrink-0" /><span>{message}</span>{retry && <button type="button" onClick={retry} className="text-button"><RefreshCw size={14} /> Thử lại</button>}</div>;
}

export function Loading({ text = 'Đang tải dữ liệu…' }: { text?: string }) {
  return <div className="loading-state" role="status"><LoaderCircle className="animate-spin" size={22} /><span>{text}</span></div>;
}

export function PriorityBadge({ priority }: { priority: Priority }) {
  const names: Record<Priority, string> = { Urgent: 'Khẩn cấp', High: 'Ưu tiên cao', Medium: 'Thông thường', 'Needs Human Review': 'Cần kiểm tra thủ công' };
  return <span className={`badge ${priority === 'Urgent' || priority === 'Needs Human Review' ? 'badge-amber' : 'badge-neutral'}`}>{names[priority] || priority}</span>;
}

export function CopyButton({ text }: { text: string }) {
  const [state, setState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  async function copy() {
    try { await navigator.clipboard.writeText(text); setState('copied'); }
    catch { setState('failed'); }
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setState('idle'), 3000);
  }
  return <div className="copy-control"><button type="button" className="text-button" onClick={copy}>{state === 'copied' ? <Check size={14} /> : <Copy size={14} />} {state === 'copied' ? 'Đã sao chép' : 'Sao chép'}</button><span className={state === 'failed' ? 'copy-error' : 'sr-only'} role="status">{state === 'failed' ? 'Không thể sao chép. Bạn có thể chọn và sao chép nội dung bên dưới.' : state === 'copied' ? 'Đã sao chép nội dung phản hồi.' : ''}</span></div>;
}
