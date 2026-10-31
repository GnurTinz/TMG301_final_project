import { useState } from 'react';
import type { TicketResult } from '../types/prediction';

const key = 'ticket-router.history.v1';
function isTicket(value: unknown): value is TicketResult {
  if (!value || typeof value !== 'object') return false;
  const ticket = value as Partial<TicketResult>;
  const decision = ticket.routing_decision;
  return typeof ticket.ticket_id === 'string' && typeof ticket.customer_message === 'string'
    && typeof ticket.customer_email === 'string' && typeof ticket.timestamp === 'string'
    && typeof ticket.automated_response === 'string' && !!decision
    && ['Payment', 'Return/Refund', 'Technical Issue'].includes(decision.category)
    && typeof decision.category_vi === 'string' && typeof decision.target_department === 'string'
    && typeof decision.dept_code === 'string'
    && typeof decision.confidence_score === 'number' && Number.isFinite(decision.confidence_score)
    && typeof decision.sla_hours === 'number' && Number.isFinite(decision.sla_hours)
    && ['Urgent', 'High', 'Medium', 'Needs Human Review'].includes(decision.priority_level)
    && !!decision.all_class_probabilities
    && ['Payment', 'Return/Refund', 'Technical Issue'].every(category => Number.isFinite(decision.all_class_probabilities[category as keyof typeof decision.all_class_probabilities]))
    && Number.isFinite(Date.parse(ticket.timestamp));
}
export function useHistory() {
  const [items, setItems] = useState<TicketResult[]>(() => {
    try {
      const stored: unknown = JSON.parse(localStorage.getItem(key) || '[]');
      return Array.isArray(stored) ? stored.filter(isTicket).slice(0, 20) : [];
    } catch { return []; }
  });
  const [storageError, setStorageError] = useState<string | null>(null);
  function save(next: TicketResult[]) {
    setItems(next);
    try { localStorage.setItem(key, JSON.stringify(next)); setStorageError(null); }
    catch { setStorageError('Trình duyệt không cho phép lưu lịch sử. Kết quả hiện tại vẫn có thể xem và sao chép.'); }
  }
  return {
    items, storageError,
    add: (ticket: TicketResult) => save([ticket, ...items.filter(i => i.ticket_id !== ticket.ticket_id)].slice(0, 20)),
    clear: () => save([]),
  };
}
