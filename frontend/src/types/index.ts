export interface Student {
  id: number;
  name: string;
  phone: string;
  group_name: string;
  monthly_fee: number;
  created_at: string;
  updated_at: string;
}

export interface StudentCreateInput {
  name: string;
  phone: string;
  group_name: string;
  monthly_fee: number;
}

export interface StudentUpdateInput {
  name?: string;
  phone?: string;
  group_name?: string;
  monthly_fee?: number;
}

export interface Payment {
  id: number;
  student_id: number;
  amount: number;
  payment_date: string;
  created_at: string;
  student_name?: string;
  group_name?: string;
}

export interface PaymentCreateInput {
  student_id: number;
  amount: number;
  payment_date: string;
}

export interface Debtor {
  student_id: number;
  name: string;
  phone: string;
  group_name: string;
  monthly_fee: number;
  total_paid: number;
  debt: number;
}

export interface MonthlyDebtorsResponse {
  month: string;
  debtors: Debtor[];
}

export interface DashboardSummary {
  month: string;
  total_students: number;
  total_expected_tuition: number;
  total_collected: number;
  total_debt: number;
  debtors_count: number;
  recent_payments: Payment[];
}
