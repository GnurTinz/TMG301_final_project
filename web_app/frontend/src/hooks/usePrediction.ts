import { useCallback, useEffect, useRef, useState } from 'react';
import { predict } from '../services/predictionApi';
import type { TicketInput, TicketResult } from '../types/prediction';

export function usePrediction() {
  const [result, setResult] = useState<TicketResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const pending = useRef<AbortController | null>(null);
  useEffect(() => () => pending.current?.abort(), []);

  const submit = useCallback(async (input: TicketInput) => {
    if (pending.current) return null;
    const controller = new AbortController();
    pending.current = controller;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const next = await predict({ message: input.message.trim(), customer_email: input.customer_email.trim() }, controller.signal);
      if (!controller.signal.aborted) { setResult(next); return next; }
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Không thể phân loại yêu cầu.');
    } finally {
      if (pending.current === controller) {
        pending.current = null;
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    return null;
  }, []);

  const reset = useCallback(() => {
    pending.current?.abort();
    pending.current = null;
    setResult(null); setError(null); setLoading(false);
  }, []);
  return { result, error, loading, submit, reset, restore: setResult };
}
