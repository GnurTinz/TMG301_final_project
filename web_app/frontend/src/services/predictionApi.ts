import type { DashboardData, Health, ModelInfo, Sample, TicketInput, TicketResult } from '../types/prediction';

const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');
export const apiUrl = (path: string) => `${baseUrl}${path}`;

export class ApiError extends Error {
  constructor(message: string, public readonly kind: 'network' | 'backend' | 'timeout', public readonly status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const timeout = AbortSignal.timeout(30_000);
  const signal = options.signal ? AbortSignal.any([options.signal, timeout]) : timeout;
  try {
    const response = await fetch(apiUrl(path), { ...options, signal, headers: { Accept: 'application/json', ...options.headers } });
    const body = await response.json().catch(() => null);
    if (!response.ok || body?.success === false) {
      throw new ApiError(body?.error || (response.status === 503 ? 'Mô hình chưa sẵn sàng. Vui lòng thử lại sau.' : `Máy chủ trả về lỗi ${response.status}.`), 'backend', response.status);
    }
    if (!body || body.success !== true) throw new ApiError('Phản hồi từ máy chủ không đúng định dạng.', 'backend');
    return body as T;
  } catch (error) {
    if (options.signal?.aborted) throw error;
    if (timeout.aborted) throw new ApiError('Yêu cầu đã quá 30 giây. Vui lòng thử lại.', 'timeout');
    if (error instanceof ApiError) throw error;
    throw new ApiError('Không thể kết nối máy chủ. Kiểm tra kết nối và thử lại.', 'network');
  }
}

export const getHealth = (signal?: AbortSignal) => request<Health>('/api/health', { signal });
export const getModelInfo = (signal?: AbortSignal) => request<ModelInfo>('/api/model-info', { signal });
export const getSamples = (signal?: AbortSignal) => request<{ success: boolean; samples: Sample[] }>('/api/samples?source=gradio', { signal });
export const getDashboard = (signal?: AbortSignal) => request<DashboardData>('/api/dashboard-data', { signal });
export async function predict(input: TicketInput, signal?: AbortSignal): Promise<TicketResult> {
  const response = await request<{ success: boolean; data: TicketResult }>('/api/route-ticket', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input), signal,
  });
  return response.data;
}
