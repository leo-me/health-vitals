export function VitalCard({
  icon,
  label,
  value,
  status,
  statusColor,
  rotation,
  offset,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  status: string;
  statusColor: string;
  rotation: string;
  offset: string;
}) {
  return (
    <div
      className={`bg-white rounded-2xl shadow-lg border border-slate-100 p-4 w-56 ${rotation} ${offset} transition-transform`}
    >
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          {label}
        </span>
      </div>
      <p className="text-xl font-bold text-slate-900">{value}</p>
      <span
        className={`mt-1 inline-block text-xs font-medium px-2 py-0.5 rounded-full ${statusColor}`}
      >
        {status}
      </span>
    </div>
  );
}