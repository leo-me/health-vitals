import { Heart, Wind, Bell, Wifi, Monitor, ArrowRight, Star, Activity, Lock } from "lucide-react";

type FeatureItem = {
  icon: React.ReactNode;
  label: string;
  bg: string;
  elevated?: boolean;
};

function FeatureCard({ icon, label, bg, elevated }: FeatureItem) {
  return (
    <div
      className={`bg-white rounded-2xl shadow-md border border-slate-100 p-5 flex flex-col items-center gap-3 transition-transform ${
        elevated ? "-translate-y-3 shadow-lg" : ""
      }`}
    >
      <div
        className={`w-12 h-12 rounded-full ${bg} flex items-center justify-center`}
      >
        {icon}
      </div>
      <span className="text-xs font-semibold text-slate-700 text-center leading-snug">
        {label}
      </span>
    </div>
  );
}


export function Features() {
  const features: FeatureItem[] = [
    {
      icon: <Heart className="w-5 h-5 text-rose-500" />,
      label: "BVP Monitoring",
      bg: "bg-rose-100",
    },
    {
      icon: <Wind className="w-5 h-5 text-sky-500" />,
      label: "EDA Signal Streaming",
      bg: "bg-sky-100",
      elevated: true,
    },
    {
      icon: <Bell className="w-5 h-5 text-amber-500" />,
      label: "Automated Alerts",
      bg: "bg-amber-100",
    },
    {
      icon: <Lock className="w-5 h-5 text-violet-500" />,
      label: "Role-Based Access",
      bg: "bg-violet-100",
    },
    {
      icon: <Wifi className="w-5 h-5 text-teal-500" />,
      label: "Stress Inference",
      bg: "bg-teal-100",
      elevated: true,
    },
    {
      icon: <Monitor className="w-5 h-5 text-slate-500" />,
      label: "Model Versioning",
      bg: "bg-slate-100",
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-6 py-24 flex flex-col lg:flex-row items-center gap-16">
      {/* Left — feature card grid */}
      <div className="flex-1 grid grid-cols-3 gap-4">
        {features.map((f) => (
          <FeatureCard key={f.label} {...f} />
        ))}
      </div>

      {/* Right — text block */}
      <div className="flex-1 lg:max-w-md">
        <h2 className="text-4xl font-extrabold text-slate-900 leading-tight mb-5">
          Continuous monitoring{" "}
          <span className="text-sky-500">episodic rounds</span>
          {" "}can&apos;t match.
        </h2>
        <p className="text-slate-500 leading-relaxed mb-8">
          Physiological signals stream continuously from Empatica E4 wristbands,
          so ML models can detect stress events the moment they arise. Results
          are routed instantly to nurses, dashboards, or alert systems — each
          consumer receiving exactly the signal it needs. When models retrain,
          downstream consumers absorb updates without interruption.
        </p>

        <div className="flex flex-wrap gap-3 mb-8">
          <a
            href="#"
            className="bg-sky-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-sky-600 transition-colors flex items-center gap-2"
          >
            See the data flow <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="#"
            className="bg-slate-900 text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-slate-800 transition-colors flex items-center gap-2"
          >
            Read the docs <ArrowRight className="w-4 h-4" />
          </a>
        </div>

        {/* Star review card */}
        <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm">
          <div className="flex gap-0.5 mb-3">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className="w-4 h-4 text-amber-400 fill-amber-400"
              />
            ))}
          </div>
          <p className="text-sm text-slate-700 leading-relaxed italic mb-3">
            &ldquo;Before Sensors2Care, we&apos;d only catch a stress episode
            during scheduled rounds — often an hour too late. The real-time
            alerts let us intervene within minutes of the wristband detecting
            a spike. For our residents with dementia, that window is
            everything.&rdquo;
          </p>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-100 flex items-center justify-center">
              <Activity className="w-4 h-4 text-sky-500" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-900">
                Miriam van den Berg
              </p>
              <p className="text-xs text-slate-500">
                Care Coordinator, De Linde Memory Care
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}