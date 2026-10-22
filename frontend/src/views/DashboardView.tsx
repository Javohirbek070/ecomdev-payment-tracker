import { useState, useEffect } from 'react';
import {
  Users,
  Coins,
  ArrowUpRight,
  AlertCircle,
  TrendingDown,
  Calendar,
  CreditCard,
  UserPlus,
  ArrowRight,
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import type { DashboardSummary } from '../types';
import { StatCard } from '../components/StatCard';
import { formatCurrency, formatDate, getCurrentMonth } from '../utils/format';

interface DashboardViewProps {
  onNavigateToStudents: () => void;
  onNavigateToPayments: () => void;
  onNavigateToDebtors: () => void;
  onOpenPaymentModal: () => void;
  onOpenAddStudentModal: () => void;
  refreshTrigger: number;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onNavigateToStudents,
  onNavigateToPayments,
  onNavigateToDebtors,
  onOpenPaymentModal,
  onOpenAddStudentModal,
  refreshTrigger,
}) => {
  const [selectedMonth, setSelectedMonth] = useState<string>(getCurrentMonth());
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async (month: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboardSummary(month);
      setSummary(data);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Ma'lumotlarni yuklashda xatolik yuz berdi");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary(selectedMonth);
  }, [selectedMonth, refreshTrigger]);

  return (
    <div className="space-y-6">
      {/* Month Filter Bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-indigo-600 shrink-0" />
          <span className="text-sm font-semibold text-slate-900">
            Hisobot davri:
          </span>
          <span className="text-sm text-slate-500 font-medium">
            {selectedMonth}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="dash-month-input" className="text-xs text-slate-500 font-medium">
            Oyni tanlash:
          </label>
          <input
            id="dash-month-input"
            type="month"
            value={selectedMonth}
            onChange={(e) => {
              if (e.target.value) {
                setSelectedMonth(e.target.value);
              }
            }}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs sm:text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
          />
          {selectedMonth !== getCurrentMonth() && (
            <button
              onClick={() => setSelectedMonth(getCurrentMonth())}
              className="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors"
            >
              Joriy oy
            </button>
          )}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
          <div>
            <div className="font-semibold">Xatolik:</div>
            <div>{error}</div>
            <button
              onClick={() => fetchSummary(selectedMonth)}
              className="mt-2 text-xs font-semibold text-rose-700 underline hover:text-rose-900"
            >
              Qayta urinish
            </button>
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Jami o'quvchilar"
          value={loading ? '...' : (summary?.total_students ?? 0)}
          subtitle="Faol ro'yxatdan o'tganlar"
          icon={<Users className="w-5 h-5" />}
          variant="default"
          onClick={onNavigateToStudents}
        />
        <StatCard
          title="Kutilayotgan to'lov"
          value={loading ? '...' : formatCurrency(summary?.total_expected_tuition)}
          subtitle={`${selectedMonth} oyi uchun reja`}
          icon={<Coins className="w-5 h-5" />}
          variant="default"
        />
        <StatCard
          title="Yig'ilgan tushum"
          value={loading ? '...' : formatCurrency(summary?.total_collected)}
          subtitle={`${selectedMonth} oyida qabul qilingan`}
          icon={<ArrowUpRight className="w-5 h-5" />}
          variant="success"
          onClick={onNavigateToPayments}
        />
        <StatCard
          title="Qoldiq qarz summasi"
          value={loading ? '...' : formatCurrency(summary?.total_debt)}
          subtitle={
            summary?.debtors_count !== undefined
              ? `${summary.debtors_count} nafar qarzdor o'quvchi`
              : 'Qarzdorlik miqdori'
          }
          icon={<TrendingDown className="w-5 h-5" />}
          variant={summary && summary.total_debt > 0 ? 'danger' : 'success'}
          onClick={onNavigateToDebtors}
        />
      </div>

      {/* Quick shortcuts banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={onOpenPaymentModal}
          className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs hover:border-emerald-500 hover:shadow-sm transition-all text-left flex items-center justify-between group"
        >
          <div className="flex items-center gap-3.5">
            <div className="p-3 rounded-lg bg-emerald-50 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-900">
                To'lov qabul qilish
              </div>
              <div className="text-xs text-slate-500">
                Yangi to'lov chekini kiritish
              </div>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 transition-colors" />
        </button>

        <button
          onClick={onOpenAddStudentModal}
          className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs hover:border-indigo-500 hover:shadow-sm transition-all text-left flex items-center justify-between group"
        >
          <div className="flex items-center gap-3.5">
            <div className="p-3 rounded-lg bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-900">
                O'quvchi ro'yxatga olish
              </div>
              <div className="text-xs text-slate-500">
                Yangi talaba va tarif qo'shish
              </div>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 transition-colors" />
        </button>

        <button
          onClick={onNavigateToDebtors}
          className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs hover:border-rose-500 hover:shadow-sm transition-all text-left flex items-center justify-between group"
        >
          <div className="flex items-center gap-3.5">
            <div className="p-3 rounded-lg bg-rose-50 text-rose-600 group-hover:bg-rose-600 group-hover:text-white transition-colors">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-900">
                Qarzdorlarni ko'rish
              </div>
              <div className="text-xs text-slate-500">
                {summary ? `${summary.debtors_count} nafar talaba to'liq to'lamagan` : 'Qarzdorlar ro\'yxati'}
              </div>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-rose-600 transition-colors" />
        </button>
      </div>

      {/* Recent Payments Section */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">
              Oxirgi to'lovlar
            </h2>
            <p className="text-xs text-slate-500">
              Eng oxirgi amalga oshirilgan 10 ta to'lov amaliyotlari
            </p>
          </div>
          <button
            onClick={onNavigateToPayments}
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
          >
            Barchasini ko'rish <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            Yuklanmoqda...
          </div>
        ) : !summary?.recent_payments || summary.recent_payments.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            Hozircha hech qanday to'lov mavjud emas.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 sm:px-6">№</th>
                  <th className="py-3 px-4 sm:px-6">O'quvchi</th>
                  <th className="py-3 px-4 sm:px-6">Guruh</th>
                  <th className="py-3 px-4 sm:px-6 text-right">Summa</th>
                  <th className="py-3 px-4 sm:px-6">To'lov sanasi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs sm:text-sm">
                {summary.recent_payments.map((p, idx) => (
                  <tr key={p.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-4 sm:px-6 font-mono text-slate-400">
                      #{idx + 1}
                    </td>
                    <td className="py-3 px-4 sm:px-6 font-medium text-slate-900">
                      {p.student_name || `Talaba #${p.student_id}`}
                    </td>
                    <td className="py-3 px-4 sm:px-6 text-slate-600">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700">
                        {p.group_name || '-'}
                      </span>
                    </td>
                    <td className="py-3 px-4 sm:px-6 text-right font-semibold text-emerald-600 tabular-nums">
                      +{formatCurrency(p.amount)}
                    </td>
                    <td className="py-3 px-4 sm:px-6 text-slate-500 tabular-nums">
                      {formatDate(p.payment_date)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
