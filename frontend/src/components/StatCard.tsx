import type { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  onClick?: () => void;
}

export const StatCard = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
  onClick,
}: StatCardProps) => {
  const variantStyles = {
    default: {
      iconBg: 'bg-indigo-50 text-indigo-600',
      valueColor: 'text-slate-900',
    },
    success: {
      iconBg: 'bg-emerald-50 text-emerald-600',
      valueColor: 'text-emerald-700',
    },
    warning: {
      iconBg: 'bg-amber-50 text-amber-600',
      valueColor: 'text-amber-700',
    },
    danger: {
      iconBg: 'bg-rose-50 text-rose-600',
      valueColor: 'text-rose-700',
    },
  }[variant];

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs transition-all ${
        onClick ? 'cursor-pointer hover:border-indigo-400 hover:shadow-sm' : 'hover:border-slate-300'
      }`}
    >
      <div className="flex items-center justify-between gap-3 mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        <div className={`p-2.5 rounded-lg ${variantStyles.iconBg}`}>
          {icon}
        </div>
      </div>
      <div className={`text-2xl font-bold tracking-tight tabular-nums ${variantStyles.valueColor}`}>
        {value}
      </div>
      {subtitle && (
        <div className="mt-1 text-xs text-slate-500 font-normal">
          {subtitle}
        </div>
      )}
    </div>
  );
};
