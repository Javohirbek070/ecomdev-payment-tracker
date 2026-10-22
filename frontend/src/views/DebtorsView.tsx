import { useState, useEffect } from 'react';
import {
  AlertCircle,
  Calendar,
  Search,
  CreditCard,
  CheckCircle2,
  TrendingDown,
  Users,
  Coins,
  X,
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import type { Debtor } from '../types';
import { formatCurrency, getCurrentMonth } from '../utils/format';

interface DebtorsViewProps {
  onRecordPaymentForDebtor: (debtor: Debtor) => void;
  refreshTrigger: number;
}

export const DebtorsView = ({
  onRecordPaymentForDebtor,
  refreshTrigger,
}: DebtorsViewProps) => {
  const [selectedMonth, setSelectedMonth] = useState<string>(getCurrentMonth());
  const [debtors, setDebtors] = useState<Debtor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchDebtors = async (month: string) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await api.getDebtors(month);
      setDebtors(resp.debtors || []);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Qarzdorlar ro'yxatini yuklashda xatolik yuz berdi");
      }
      setDebtors([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDebtors(selectedMonth);
  }, [selectedMonth, refreshTrigger]);

  const filteredDebtors = debtors.filter((d) => {
    const q = searchQuery.toLowerCase();
    return (
      d.name.toLowerCase().includes(q) ||
      d.phone.toLowerCase().includes(q) ||
      d.group_name.toLowerCase().includes(q)
    );
  });

  const totalDebtSum = filteredDebtors.reduce((acc, d) => acc + (Number(d.debt) || 0), 0);
  const totalPaidSum = filteredDebtors.reduce((acc, d) => acc + (Number(d.total_paid) || 0), 0);

  return (
    <div className="space-y-6">
      {/* Month Selector Bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-rose-600 shrink-0" />
          <span className="text-sm font-semibold text-slate-900">
            Qarzdorlik davri:
          </span>
          <span className="text-sm text-slate-500 font-medium">
            {selectedMonth} oyi bo'yicha
          </span>
        </div>

        <div className="flex items-center gap-2">
          <label htmlFor="debtor-month-input" className="text-xs text-slate-500 font-medium">
            Oyni o'zgartirish:
          </label>
          <input
            id="debtor-month-input"
            type="month"
            value={selectedMonth}
            onChange={(e) => {
              if (e.target.value) {
                setSelectedMonth(e.target.value);
              }
            }}
            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs sm:text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-600"
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

      {/* Summary KPI Cards for Debtors */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs uppercase font-semibold text-slate-400">
              Qarzdor o'quvchilar
            </span>
            <div className="text-2xl font-bold text-slate-900 tabular-nums mt-1">
              {loading ? '...' : filteredDebtors.length} nafar
            </div>
          </div>
          <div className="p-2.5 rounded-lg bg-rose-50 text-rose-600">
            <Users className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs uppercase font-semibold text-slate-400">
              Qoldiq qarz summasi
            </span>
            <div className="text-2xl font-bold text-rose-600 tabular-nums mt-1">
              {loading ? '...' : formatCurrency(totalDebtSum)}
            </div>
          </div>
          <div className="p-2.5 rounded-lg bg-rose-50 text-rose-600">
            <TrendingDown className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs uppercase font-semibold text-slate-400">
              Qisman to'langan summa
            </span>
            <div className="text-2xl font-bold text-amber-600 tabular-nums mt-1">
              {loading ? '...' : formatCurrency(totalPaidSum)}
            </div>
          </div>
          <div className="p-2.5 rounded-lg bg-amber-50 text-amber-600">
            <Coins className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
          <div>
            <div className="font-semibold">Xatolik:</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 shadow-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Qarzdor ismi, telefon yoki guruhi..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-600"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Debtors Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            Qarzdorlar ro'yxati hisoblanmoqda...
          </div>
        ) : filteredDebtors.length === 0 ? (
          <div className="p-12 text-center space-y-2">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 mx-auto flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-800">
              Qarzdorlar yo'q!
            </h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              {searchQuery
                ? "Qidiruv so'rovi bo'yicha hech qanday qarzdor topilmadi."
                : `${selectedMonth} oyi uchun barcha o'quvchilar to'lovlarni to'liq amalga oshirishgan.`}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 sm:px-6">ID</th>
                  <th className="py-3 px-4 sm:px-6">O'quvchi F.I.Sh</th>
                  <th className="py-3 px-4 sm:px-6">Telefon raqam</th>
                  <th className="py-3 px-4 sm:px-6">Guruh</th>
                  <th className="py-3 px-4 sm:px-6 text-right">Oylik tarif</th>
                  <th className="py-3 px-4 sm:px-6 text-right">To'langan</th>
                  <th className="py-3 px-4 sm:px-6 text-right">Qoldiq qarz</th>
                  <th className="py-3 px-4 sm:px-6 text-center">Holat</th>
                  <th className="py-3 px-4 sm:px-6 text-center">Amal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs sm:text-sm">
                {filteredDebtors.map((d) => {
                  const hasPartial = Number(d.total_paid) > 0;
                  return (
                    <tr key={d.student_id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="py-3.5 px-4 sm:px-6 font-mono text-slate-400">
                        #{d.student_id}
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 font-semibold text-slate-900">
                        {d.name}
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-slate-600 tabular-nums">
                        {d.phone}
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-slate-700">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700">
                          {d.group_name}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-right font-medium text-slate-700 tabular-nums">
                        {formatCurrency(d.monthly_fee)}
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-right font-medium text-slate-900 tabular-nums">
                        {formatCurrency(d.total_paid)}
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-right font-bold text-rose-600 tabular-nums">
                        {formatCurrency(d.debt)}
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-center">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            hasPartial
                              ? 'bg-amber-50 text-amber-700 border border-amber-200/60'
                              : 'bg-rose-50 text-rose-700 border border-rose-200/60'
                          }`}
                        >
                          {hasPartial ? "Qisman to'langan" : "To'lanmagan"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 sm:px-6 text-center">
                        <button
                          onClick={() => onRecordPaymentForDebtor(d)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-xs font-medium transition-colors"
                          title="To'lov kiritish"
                        >
                          <CreditCard className="w-3.5 h-3.5" />
                          <span>To'lash</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
