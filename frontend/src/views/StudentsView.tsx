import { useState, useEffect } from 'react';
import {
  Search,
  Plus,
  Edit2,
  Trash2,
  Eye,
  AlertCircle,
  CreditCard,
  Phone,
  BookOpen,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import type { Student, Payment } from '../types';
import { Modal } from '../components/Modal';
import { ConfirmModal } from '../components/ConfirmModal';
import { formatCurrency, formatDate } from '../utils/format';

interface StudentsViewProps {
  onRecordPaymentForStudent: (student: Student) => void;
  refreshTrigger: number;
  onDataChanged: () => void;
  isAddModalOpenFromHeader?: boolean;
  onCloseAddModalFromHeader?: () => void;
}

export const StudentsView = ({
  onRecordPaymentForStudent,
  refreshTrigger,
  onDataChanged,
  isAddModalOpenFromHeader = false,
  onCloseAddModalFromHeader,
}: StudentsViewProps) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState<boolean>(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [viewingStudent, setViewingStudent] = useState<Student | null>(null);
  const [studentPayments, setStudentPayments] = useState<Payment[]>([]);
  const [loadingPayments, setLoadingPayments] = useState<boolean>(false);
  const [deletingStudent, setDeletingStudent] = useState<Student | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Form fields
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    group_name: '',
    monthly_fee: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Sync header add modal trigger
  useEffect(() => {
    if (isAddModalOpenFromHeader) {
      resetForm();
      setIsAddModalOpen(true);
    }
  }, [isAddModalOpenFromHeader]);

  const fetchStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStudents();
      setStudents(data);
    } catch (err: any) {
      setError(err?.message || "O'quvchilar ro'yxatini yuklashda xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [refreshTrigger]);

  const resetForm = () => {
    setFormData({
      name: '',
      phone: '',
      group_name: '',
      monthly_fee: '',
    });
    setActionError(null);
  };

  const handleOpenAdd = () => {
    resetForm();
    setIsAddModalOpen(true);
  };

  const handleOpenEdit = (student: Student) => {
    setActionError(null);
    setEditingStudent(student);
    setFormData({
      name: student.name,
      phone: student.phone,
      group_name: student.group_name,
      monthly_fee: String(student.monthly_fee),
    });
  };

  const handleOpenView = async (student: Student) => {
    setViewingStudent(student);
    setLoadingPayments(true);
    try {
      const payments = await api.getStudentPayments(student.id);
      setStudentPayments(payments);
    } catch {
      setStudentPayments([]);
    } finally {
      setLoadingPayments(false);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);

    const feeNum = parseFloat(formData.monthly_fee);
    if (isNaN(feeNum) || feeNum <= 0) {
      setActionError("Oylik to'lov summasi musbat raqam bo'lishi shart");
      return;
    }

    if (!formData.name.trim() || !formData.phone.trim() || !formData.group_name.trim()) {
      setActionError("Barcha maydonlarni to'ldirish majburiy");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.createStudent({
        name: formData.name.trim(),
        phone: formData.phone.trim(),
        group_name: formData.group_name.trim(),
        monthly_fee: feeNum,
      });
      setIsAddModalOpen(false);
      if (onCloseAddModalFromHeader) onCloseAddModalFromHeader();
      resetForm();
      fetchStudents();
      onDataChanged();
    } catch (err: any) {
      setActionError(err?.message || "O'quvchini qo'shishda xatolik yuz berdi");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingStudent) return;
    setActionError(null);

    const feeNum = parseFloat(formData.monthly_fee);
    if (isNaN(feeNum) || feeNum <= 0) {
      setActionError("Oylik to'lov summasi musbat raqam bo'lishi shart");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.updateStudent(editingStudent.id, {
        name: formData.name.trim(),
        phone: formData.phone.trim(),
        group_name: formData.group_name.trim(),
        monthly_fee: feeNum,
      });
      setEditingStudent(null);
      resetForm();
      fetchStudents();
      onDataChanged();
    } catch (err: any) {
      setActionError(err?.message || "Ma'lumotlarni yangilashda xatolik yuz berdi");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingStudent) return;
    setIsDeleting(true);
    setActionError(null);
    try {
      await api.deleteStudent(deletingStudent.id);
      setDeletingStudent(null);
      fetchStudents();
      onDataChanged();
    } catch (err: any) {
      setActionError(err?.message || "O'quvchini o'chirishda xatolik yuz berdi");
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredStudents = students.filter((s) => {
    const q = searchQuery.toLowerCase();
    return (
      s.name.toLowerCase().includes(q) ||
      s.phone.toLowerCase().includes(q) ||
      s.group_name.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Top action & search bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Ism, telefon yoki guruh bo'yicha qidirish..."
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
            Jami: <strong className="text-slate-800">{filteredStudents.length}</strong> ta o'quvchi
          </span>
          <button
            onClick={handleOpenAdd}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>O'quvchi qo'shish</span>
          </button>
        </div>
      </div>

      {/* Global alert error if delete blocked */}
      {actionError && !isAddModalOpen && !editingStudent && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
          <div className="flex-1">
            <div className="font-semibold">Amal bajarilmadi:</div>
            <div>{actionError}</div>
          </div>
          <button
            onClick={() => setActionError(null)}
            className="text-rose-500 hover:text-rose-700"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Students Table */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            O'quvchilar ro'yxati yuklanmoqda...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 text-sm">{error}</div>
        ) : filteredStudents.length === 0 ? (
          <div className="p-12 text-center text-slate-400 space-y-2">
            <p className="text-base font-medium text-slate-700">O'quvchilar topilmadi</p>
            <p className="text-xs">
              {searchQuery
                ? "Qidiruv so'rovi bo'yicha hech qanday natija topilmadi."
                : "Hozircha o'quvchilar mavjud emas. Yangi o'quvchi qo'shish uchun yuqoridagi tugmani bosing."}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-100 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 sm:px-6">ID</th>
                  <th className="py-3 px-4 sm:px-6">F.I.Sh</th>
                  <th className="py-3 px-4 sm:px-6">Telefon raqam</th>
                  <th className="py-3 px-4 sm:px-6">Guruh</th>
                  <th className="py-3 px-4 sm:px-6 text-right">Oylik to'lov</th>
                  <th className="py-3 px-4 sm:px-6">Ro'yxatdan o'tgan</th>
                  <th className="py-3 px-4 sm:px-6 text-center">Amallar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs sm:text-sm">
                {filteredStudents.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3.5 px-4 sm:px-6 font-mono text-slate-400">
                      #{s.id}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 font-semibold text-slate-900">
                      {s.name}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-slate-600 tabular-nums">
                      {s.phone}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-slate-700">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200/60">
                        {s.group_name}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-right font-medium text-slate-900 tabular-nums">
                      {formatCurrency(s.monthly_fee)}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-slate-500 tabular-nums">
                      {formatDate(s.created_at)}
                    </td>
                    <td className="py-3.5 px-4 sm:px-6 text-center">
                      <div className="flex items-center justify-center gap-1.5">
                        <button
                          onClick={() => handleOpenView(s)}
                          className="p-1.5 rounded-md text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                          title="Tafsilotlar va to'lov tarixi"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onRecordPaymentForStudent(s)}
                          className="p-1.5 rounded-md text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                          title="To'lov kiritish"
                        >
                          <CreditCard className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleOpenEdit(s)}
                          className="p-1.5 rounded-md text-slate-500 hover:text-amber-600 hover:bg-amber-50 transition-colors"
                          title="Tahrirlash"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setActionError(null);
                            setDeletingStudent(s);
                          }}
                          className="p-1.5 rounded-md text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="O'chirish"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Student Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => {
          setIsAddModalOpen(false);
          if (onCloseAddModalFromHeader) onCloseAddModalFromHeader();
          resetForm();
        }}
        title="Yangi o'quvchi qo'shish"
        subtitle="Markazga yangi o'quvchi ma'lumotlari va to'lov tarifini kiriting"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          {actionError && (
            <div className="p-3 rounded-lg bg-rose-50 text-rose-700 text-xs border border-rose-200">
              {actionError}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              F.I.Sh (To'liq ism) *
            </label>
            <input
              type="text"
              required
              placeholder="Masalan: Sardor Rahimov"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Telefon raqami *
            </label>
            <input
              type="text"
              required
              placeholder="+998901234567"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Guruh nomi *
            </label>
            <input
              type="text"
              required
              placeholder="Masalan: Backend Python-1"
              value={formData.group_name}
              onChange={(e) => setFormData({ ...formData, group_name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Oylik to'lov summasi (so'mda) *
            </label>
            <input
              type="number"
              required
              min="1000"
              step="1000"
              placeholder="800000"
              value={formData.monthly_fee}
              onChange={(e) => setFormData({ ...formData, monthly_fee: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 tabular-nums"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => {
                setIsAddModalOpen(false);
                if (onCloseAddModalFromHeader) onCloseAddModalFromHeader();
                resetForm();
              }}
              className="px-4 py-2 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting && (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              )}
              Saqlash
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Student Modal */}
      <Modal
        isOpen={!!editingStudent}
        onClose={() => {
          setEditingStudent(null);
          resetForm();
        }}
        title="O'quvchi ma'lumotlarini tahrirlash"
        subtitle={`ID: #${editingStudent?.id}`}
      >
        <form onSubmit={handleEditSubmit} className="space-y-4">
          {actionError && (
            <div className="p-3 rounded-lg bg-rose-50 text-rose-700 text-xs border border-rose-200">
              {actionError}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              F.I.Sh (To'liq ism) *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Telefon raqami *
            </label>
            <input
              type="text"
              required
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Guruh nomi *
            </label>
            <input
              type="text"
              required
              value={formData.group_name}
              onChange={(e) => setFormData({ ...formData, group_name: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Oylik to'lov summasi (so'mda) *
            </label>
            <input
              type="number"
              required
              min="1000"
              step="1000"
              value={formData.monthly_fee}
              onChange={(e) => setFormData({ ...formData, monthly_fee: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 tabular-nums"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => {
                setEditingStudent(null);
                resetForm();
              }}
              className="px-4 py-2 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmitting && (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              )}
              Yangilash
            </button>
          </div>
        </form>
      </Modal>

      {/* Student Details & Payment History Modal */}
      <Modal
        isOpen={!!viewingStudent}
        onClose={() => setViewingStudent(null)}
        title="O'quvchi ma'lumotlari va to'lov tarixi"
        subtitle={`ID: #${viewingStudent?.id}`}
        maxWidth="lg"
      >
        {viewingStudent && (
          <div className="space-y-6">
            {/* Student Info Card */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm">
              <div>
                <span className="text-slate-400 block text-xs">F.I.Sh:</span>
                <span className="font-semibold text-slate-900">{viewingStudent.name}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Telefon:</span>
                <span className="font-medium text-slate-800 flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  {viewingStudent.phone}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Guruh:</span>
                <span className="font-medium text-slate-800 flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                  {viewingStudent.group_name}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Oylik to'lov tarifi:</span>
                <span className="font-semibold text-indigo-700 tabular-nums">
                  {formatCurrency(viewingStudent.monthly_fee)}
                </span>
              </div>
            </div>

            {/* Payment history list */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-slate-900">
                  Amalga oshirilgan to'lovlar tarixi
                </h4>
                <button
                  onClick={() => {
                    const s = viewingStudent;
                    setViewingStudent(null);
                    onRecordPaymentForStudent(s);
                  }}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-600 hover:text-emerald-700"
                >
                  <Plus className="w-3.5 h-3.5" /> To'lov kiritish
                </button>
              </div>

              {loadingPayments ? (
                <div className="p-6 text-center text-slate-400 text-xs">
                  To'lovlar tarixi yuklanmoqda...
                </div>
              ) : studentPayments.length === 0 ? (
                <div className="p-6 text-center text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-xs">
                  Ushbu o'quvchi tomonidan hali to'lovlar amalga oshirilmagan.
                </div>
              ) : (
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                        <th className="py-2.5 px-3">Chek ID</th>
                        <th className="py-2.5 px-3 text-right">Summa</th>
                        <th className="py-2.5 px-3">To'lov sanasi</th>
                        <th className="py-2.5 px-3">Kiritilgan vaqt</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {studentPayments.map((p) => (
                        <tr key={p.id}>
                          <td className="py-2.5 px-3 font-mono text-slate-400">#{p.id}</td>
                          <td className="py-2.5 px-3 text-right font-semibold text-emerald-600 tabular-nums">
                            +{formatCurrency(p.amount)}
                          </td>
                          <td className="py-2.5 px-3 text-slate-700 tabular-nums">
                            {formatDate(p.payment_date)}
                          </td>
                          <td className="py-2.5 px-3 text-slate-400 tabular-nums">
                            {formatDate(p.created_at)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={!!deletingStudent}
        onClose={() => setDeletingStudent(null)}
        onConfirm={handleDeleteConfirm}
        isLoading={isDeleting}
        title="O'quvchini o'chirish"
        message={`"${deletingStudent?.name}" o'quvchisini tizimdan o'chirishni tasdiqlaysizmi? Eslatma: agar o'quvchining to'lov tarixi mavjud bo'lsa, moliyaviy hisobot butunligini ta'minlash uchun o'chirish rad etiladi.`}
      />
    </div>
  );
};
