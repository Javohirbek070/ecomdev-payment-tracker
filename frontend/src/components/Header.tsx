import { Menu, Plus, RefreshCw, CreditCard } from 'lucide-react';
import type { TabType } from './Sidebar';

interface HeaderProps {
  currentTab: TabType;
  onOpenMobileMenu: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
  onAddStudent: () => void;
  onRecordPayment: () => void;
}

export const Header = ({
  currentTab,
  onOpenMobileMenu,
  onRefresh,
  isRefreshing,
  onAddStudent,
  onRecordPayment,
}: HeaderProps) => {
  const titles: Record<TabType, { title: string; subtitle: string }> = {
    dashboard: {
      title: 'Boshqaruv paneli',
      subtitle: "O'quv markazining umumiy moliyaviy va to'lov ko'rsatkichlari",
    },
    students: {
      title: "O'quvchilar",
      subtitle: "Barcha ro'yxatdan o'tgan o'quvchilar, guruhlar va to'lov tariflari",
    },
    payments: {
      title: "To'lovlar",
      subtitle: "O'quvchilar tomonidan amalga oshirilgan barcha to'lovlar tarixi",
    },
    debtors: {
      title: 'Qarzdorlar',
      subtitle: "Oylik to'lovini to'liq to'lamagan o'quvchilar monitoringi",
    },
  };

  const { title, subtitle } = titles[currentTab];

  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenMobileMenu}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 lg:hidden focus:outline-none"
            aria-label="Menyuni ochish"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight leading-tight">
              {title}
            </h1>
            <p className="hidden sm:block text-xs text-slate-500 font-normal">
              {subtitle}
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors disabled:opacity-50"
            title="Ma'lumotlarni yangilash"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-indigo-600' : ''}`} />
          </button>

          <button
            onClick={onRecordPayment}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-600 text-white text-xs sm:text-sm font-medium hover:bg-emerald-700 transition-colors shadow-xs"
          >
            <CreditCard className="w-4 h-4" />
            <span className="hidden xs:inline">To'lov qabul qilish</span>
          </button>

          <button
            onClick={onAddStudent}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-indigo-600 text-white text-xs sm:text-sm font-medium hover:bg-indigo-700 transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden xs:inline">O'quvchi qo'shish</span>
          </button>
        </div>
      </div>
    </header>
  );
};
