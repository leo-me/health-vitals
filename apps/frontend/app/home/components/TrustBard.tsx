export function TrustBar() {
  const stack = ["Empatica E4", "FastAPI", "PostgreSQL", "Docker", "Python", "scikit-learn"];
  return (
    <section className="border-y border-slate-100 bg-slate-50 py-6">
      <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-center gap-6">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
          Built on
        </span>
        <div className="flex flex-wrap items-center gap-3">
          {stack.map((item) => (
            <span
              key={item}
              className="text-xs font-semibold text-slate-600 border border-slate-200 bg-white px-3 py-1.5 rounded-full shadow-sm"
            >
              {item}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}