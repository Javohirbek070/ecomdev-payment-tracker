import type {
  Student,
  StudentCreateInput,
  StudentUpdateInput,
  Payment,
  PaymentCreateInput,
  MonthlyDebtorsResponse,
  DashboardSummary,
} from '../types';

const getBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    // When running on Vite dev server (typically port 5173), route to local backend
    if (window.location.port === '5173') {
      return (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');
    }
    // When served on production (e.g., Vercel or FastAPI static server), use relative URL (same origin)
    return '';
  }
  return '';
};

const BASE_URL = getBaseUrl();

class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options?.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      let message = 'Server xatosi yuz berdi';
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          message = data.detail;
        } else if (Array.isArray(data.detail)) {
          message = data.detail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
        }
      }
      throw new ApiError(message, response.status, data);
    }

    return data as T;
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error?.message || "Server bilan bog'lanishda xatolik yuz berdi. Backend ishlayotganligini tekshiring.",
      0
    );
  }
}

export const api = {
  // Dashboard
  getDashboardSummary: (month?: string) => {
    const q = month ? `?month=${encodeURIComponent(month)}` : '';
    return request<DashboardSummary>(`/dashboard/summary${q}`);
  },

  // Students
  getStudents: () => request<Student[]>('/students'),
  getStudent: (id: number) => request<Student>(`/students/${id}`),
  createStudent: (data: StudentCreateInput) =>
    request<Student>('/students', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateStudent: (id: number, data: StudentUpdateInput) =>
    request<Student>(`/students/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteStudent: (id: number) =>
    request<void>(`/students/${id}`, {
      method: 'DELETE',
    }),

  // Payments
  getPayments: (limit = 50) => request<Payment[]>(`/payments?limit=${limit}`),
  getStudentPayments: (studentId: number) =>
    request<Payment[]>(`/students/${studentId}/payments`),
  createPayment: (data: PaymentCreateInput) =>
    request<Payment>('/payments', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Debtors
  getDebtors: (month: string) =>
    request<MonthlyDebtorsResponse>(`/debtors?month=${encodeURIComponent(month)}`),
};

export { ApiError };
