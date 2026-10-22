import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  AlertCircle,
  CheckCircle2,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import type { Payment, Student } from '../types';
import { Modal } from '../components/Modal';
import { formatCurrency, formatDate, getTodayDate } from '../utils/format';

interface PaymentsViewProps {
  refreshTrigger: number;
  onDataChanged: () => void;
  preselectedStudent?: Student | null;
  onClearPreselectedStudent?: () => void;
  isCreateModalOpenFromHeader?: boolean;
  onCloseCreateModalFromHeader?: () => void;
}

export const PaymentsView = ({
  refreshTrigger,
  onDataChanged,
  preselectedStudent,
  onClearPreselectedStudent,
  isCreateModalOpenFromHeader = false,
  onCloseCreateModalFromHeader,
}: PaymentsViewProps) => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Payment form state
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [paymentDate, setPaymentDate] = useState<string>(getTodayDate());
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  // Sync header or parent modal triggers
  useEffect(() => {
    if (isCreateModalOpenFromHeader) {
      resetForm();
      setIsModalOpen(true);
    }
  }, [isCreateModalOpenFromHeader]);

  useEffect(() => {
    if (preselectedStudent) {
      resetForm();
      setSelectedStudentId(String(preselectedStudent.id));
      setAmount(String(preselectedStudent.monthly_fee));
      setIsModalOpen(true);
    }
  }, [preselectedStudent]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [paymentsData, studentsData] = await Promise.all([
        api.getPayments(100),
        api.getStudents(),
      ]);
      setPayments(paymentsData);
      setStudents(studentsData);
    } catch (err: any) {
      setError(err?.message || "To'lovlar ro'yxatini yuklashda xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [refreshTrigger]);

  const resetForm = () => {
    setSelectedStudentId('');
    setAmount('');
    setPaymentDate(getTodayDate());
    setFormError(null);
    setFormSuccess(null);
  };

  const handleOpenModal = () => {
    resetForm();
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    if (onClearPreselectedStudent) onClearPreselectedStudent();
    if (onCloseCreateModalFromHeader) onCloseCreateModalFromHeader();
    resetForm();
  };

  const handleStudentSelectChange = (studentId: string) => {
    setSelectedStudentId(studentId);
    setFormError(null);
    const student = students.find((s) => String(s.id) === studentId);
    if (student) {
      setAmount(String(student.monthly_fee));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    const sId = parseInt(selectedStudentId, 10);
    if (isNaN(sId) || sId <= 0) {
      setFormError("Iltimos, o'quvchini tanlang");
      return;
    }

    const amtNum = parseFloat(amount);
    if (isNaN(amtNum) || amtNum <= 0) {
      setFormError("To'lov summasi musbat raqam bo'lishi shart");
      return;
    }

    if (!paymentDate) {
      setFormError("To'lov sanasini tanlang");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.createPayment({
        student_id: sId,
        amount: amtNum,
        payment_date: paymentDate,
      });

      setFormSuccess("To'lov muvaffaqiyatli qabul qilindi va tizimga yozildi!");
      setTimeout(() => {
        handleCloseModal();
        fetchData();
        onDataChanged();
      }, 1200);
    } catch (err: any) {
      setFormError(err?.message || "To'lovni qabul qilishda xatolik yuz berdi");
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredPayments = payments.filter((p) => {
    const q = searchQuery.toLowerCase();
    const studentName = p.student_name?.toLowerCase() || '';
    const groupName = p.group_name?.toLowerCase() || '';
    return (
      studentName.includes(q) ||
      groupName.includes(q) ||
      String(p.student_id).includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Top action and filter bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="O'quvchi ismi yoki guruh bo'yicha qidirish..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
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

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <span className="text-xs text-slate-500">
            Jami: <strong className="text-slate-800">{filteredPayments.length}</strong> ta to'lov
          </span>
          <button
            onClick={handleOpenModal}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>To'lov qabul qilish</span>
          </button>
        </div>
      </div>

      {/* Payments Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            To'lovlar ro'yxati yuklanmoqda...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-sm">{error}</div>
        ) : filteredPayments.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-2">
            <p className="text-base font-medium text-slate-700">To'lovlar mavjud emas</p>
            <p className="text-xs">
              {searchQuery
                ? "Qidiruv bo'yicha hech qanday to'lov cheki topilmadi."
                : "Hozircha tizimda to'lovlar qayd etilmagan."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 sm:px-6">Chek ID</th>
                  <th className="py-3 px-4 sm:px-6">O'quvchi</th>
                  <th className="py-3 px-4 sm:px-6">Guruh</th>
                  <th className="py-3 px-4 sm:px-6 text-right">To'lov summasi</th>
                  <th className="py-3 px-4 sm:px-6">To'lov sanasi</th>
                  <th className="py-3 px-4 sm:px-6">Qayd etilgan vaqt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs sm:text-sm">
                {filteredPayments.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3.5 px-4 sm:px-6 font-mono text-slate-400 font-medium">
                      #{p.id}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 font-semibold text-slate-900">
                      {p.student_name || `O'quvchi #${p.student_id}`}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-slate-700">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700">
                        {p.group_name || '-'}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-right font-bold text-emerald-600 tabular-nums">
                      +{formatCurrency(p.amount)}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-slate-700 tabular-nums">
                      {formatDate(p.payment_date)}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-slate-400 tabular-nums text-xs">
                      {formatDate(p.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Record Payment Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title="Yangi to'lov qabul qilish"
        subtitle="O'quvchi uchun to'lov summasi va sanasini kiriting"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-rose-50 text-rose-700 text-xs border border-rose-200 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{formError}</span>
            </div>
          )}

          {formSuccess && (
            <div className="p-3 rounded-lg bg-emerald-50 text-emerald-700 text-xs border border-emerald-200 flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{formSuccess}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              O'quvchini tanlang *
            </label>
            <select
              required
              value={selectedStudentId}
              onChange={(e) => handleStudentSelectChange(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 bg-white"
            >
              <option value="">-- O'quvchini tanlang --</option>
              {students.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.group_name}) — {formatCurrency(s.monthly_fee)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              To'lov summasi (so'mda) *
            </label>
            <input
              type="number"
              required
              min="1000"
              step="1000"
              placeholder="Masalan: 500000"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 tabular-nums"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              To'lov sanasi *
            </label>
            <input
              type="date"
              required
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 tabular-nums"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={handleCloseModal}
              className="px-4 py-2 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !!formSuccess}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting && (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              )}
              To'lovni tasdiqlash
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
