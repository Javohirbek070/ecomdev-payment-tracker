import type { ReactNode } from 'react';
import {
  LayoutDashboard,
  Users,
  CreditCard,
  AlertCircle,
  X,
  GraduationCap,
} from 'lucide-react';

export type TabType = 'dashboard' | 'students' | 'payments' | 'debtors';

interface SidebarProps {
  currentTab: TabType;
  onTabChange: (tab: TabType) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar = ({
  currentTab,
  onTabChange,
  isOpen,
  onClose,
}: SidebarProps) => {
  const navItems: { id: TabType; label: string; icon: ReactNode; desc: string }[] = [
    {
      id: 'dashboard',
      label: 'Boshqaruv paneli',
      desc: 'Umumiy moliyaviy hisobot',
      icon: <LayoutDashboard className="w-5 h-5" />,
    },
    {
      id: 'students',
      label: "O'quvchilar",
      desc: "Talabalar ro'yxati va boshqaruvi",
      icon: <Users className="w-5 h-5" />,
    },
    {
      id: 'payments',
      label: "To'lovlar",
      desc: "To'lov kiritish va tarixi",
      icon: <CreditCard className="w-5 h-5" />,
    },
    {
      id: 'debtors',
      label: 'Qarzdorlar',
      desc: 'Oylik qarzdorlik tahlili',
      icon: <AlertCircle className="w-5 h-5" />,
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-slate-200 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand header */}
        <div className="h-16 px-6 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-xs">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="font-semibold text-slate-900 leading-tight">Ecomdev</div>
              <div className="text-xs text-slate-500 font-medium">O'quv Markazi</div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 lg:hidden"
            aria-label="Menyuni yopish"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          <div className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Asosiy menyu
          </div>
          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  onClose();
                }}
                className={`w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors text-left ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <span className={isActive ? 'text-indigo-600' : 'text-slate-400'}>
                  {item.icon}
                </span>
                <div className="flex-1 truncate">
                  <div className="leading-snug">{item.label}</div>
                  <div className="text-[11px] text-slate-400 font-normal truncate">
                    {item.desc}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer info */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="bg-white p-3 rounded-lg border border-slate-200/80 text-xs text-slate-600 space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-medium text-slate-700">Tizim holati:</span>
              <span className="inline-flex items-center gap-1.5 text-emerald-600 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Faol
              </span>
            </div>
            <div className="text-[11px] text-slate-400">Telegram Bot & API integratsiyalangan</div>
          </div>
        </div>
      </aside>
    </>
  );
};
