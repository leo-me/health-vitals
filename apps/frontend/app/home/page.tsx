import {
  Shield,
  Heart,
  Wind,
  Bell,
  Lock,
  Wifi,
  Monitor,
  ArrowRight,
  Star,
  Activity,
  ExternalLink,
  ActivityIcon,
} from "lucide-react";

// ─── Navbar ──────────────────────────────────────────────────────────────────

function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-slate-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          {/* <div className="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center">
            <Shield className="w-4 h-4 text-white" />
          </div> */}
          <div className="w-6 h-6 rounded-lg bg-sky-500 flex items-center justify-center">
            <ActivityIcon className="w-4 h-4 text-white" />
          </div>
          <span className="text-lg font-bold text-slate-900 tracking-tight">
            Sensors2Care
          </span>
        </div>

        {/* Nav links */}
        <div className="hidden md:flex items-center gap-8">
          {["Features", "Architecture", "Data", "Docs"].map((link) => (
            <a
              key={link}
              href="#"
              className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
              {link}
            </a>
          ))}
        </div>

        {/* CTA buttons */}
        <div className="flex items-center gap-3">
          <a
            href="#"
            className="text-sm text-slate-700 hover:text-slate-900 font-medium flex items-center gap-1 transition-colors"
          >
            Sign in <ArrowRight className="w-3.5 h-3.5" />
          </a>
          <a
            href="#"
            className="text-sm bg-slate-900 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-800 transition-colors flex items-center gap-1"
          >
            Get started <ArrowRight className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </nav>
  );
}

// ─── Floating vital cards ─────────────────────────────────────────────────────

function VitalCard({
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

// ─── Hero ─────────────────────────────────────────────────────────────────────

function Hero() {
  return (
    <section className="max-w-7xl mx-auto px-6 pt-20 pb-24 flex flex-col lg:flex-row items-center gap-16">
      {/* Left — text */}
      <div className="flex-1 lg:w-3/5">
        {/* Live badge */}
        <div className="inline-flex items-center gap-2 bg-rose-50 border border-rose-100 text-rose-600 text-xs font-semibold px-3 py-1.5 rounded-full mb-6">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
          Live inference · Empatica E4 · Stress detection
        </div>

        <h1 className="text-5xl lg:text-6xl font-extrabold text-slate-900 leading-tight tracking-tight mb-6">
          Real-time stress detection{" "}
          <span className="text-sky-500">for patients</span>
          <br />
          who can&apos;t self-report
        </h1>

        <p className="text-lg text-slate-500 leading-relaxed mb-8 max-w-xl">
          EDA and BVP signals stream continuously from Empatica E4 wristbands,
          feeding ML models that detect stress and route results to nurses,
          dashboards, and alert systems in real time. Built for dementia and
          chronic condition care, where episodic assessment misses the moments
          that matter most.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-wrap items-center gap-3 mb-10">
          <a
            href="#"
            className="bg-slate-900 text-white px-6 py-3 rounded-xl font-semibold text-sm hover:bg-slate-800 transition-colors flex items-center gap-2"
          >
            Explore the platform <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="#"
            className="border-2 border-amber-400 text-amber-600 px-6 py-3 rounded-xl font-semibold text-sm hover:bg-amber-50 transition-colors flex items-center gap-2"
          >
            View architecture <ArrowRight className="w-4 h-4" />
          </a>
        </div>

        {/* Trust logos */}
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs text-slate-400 font-medium uppercase tracking-wide">
            Trusted by care teams at
          </span>
          {["St. Mary's Clinic", "HealthBridge", "MedCore Network"].map((name) => (
            <span
              key={name}
              className="text-xs font-semibold text-slate-600 bg-slate-100 border border-slate-200 px-3 py-1 rounded-full"
            >
              {name}
            </span>
          ))}
        </div>
      </div>

      {/* Right — floating vital cards */}
      <div className="relative flex-1 lg:w-2/5 h-80 lg:h-96 flex items-center justify-center">
        {/* Card 1 — BVP Signal */}
        <div className="absolute top-0 right-4 rotate-2 shadow-xl">
          <VitalCard
            icon={<Heart className="w-4 h-4 text-rose-500" />}
            label="BVP Signal"
            value="68 bpm"
            status="Streaming"
            statusColor="bg-emerald-100 text-emerald-700"
            rotation=""
            offset=""
          />
        </div>

        {/* Card 2 — EDA Level */}
        <div className="absolute top-28 left-0 -rotate-2 shadow-xl">
          <VitalCard
            icon={<Wind className="w-4 h-4 text-sky-500" />}
            label="EDA Level"
            value="4.2 μS"
            status="Elevated"
            statusColor="bg-amber-100 text-amber-700"
            rotation=""
            offset=""
          />
        </div>

        {/* Card 3 — Stress Alert */}
        <div className="absolute bottom-0 right-8 rotate-1 shadow-xl">
          <div className="bg-white rounded-2xl shadow-lg border border-rose-100 p-4 w-64">
            <div className="flex items-center gap-2 mb-2">
              <Bell className="w-4 h-4 text-amber-500" />
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Inference Alert
              </span>
            </div>
            <p className="text-sm font-bold text-slate-900">
              ⚠️ Stress event detected
            </p>
            <p className="text-xs text-slate-500 mt-1">Patient 07 · Just now</p>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── Trust bar ────────────────────────────────────────────────────────────────

function TrustBar() {
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

// ─── Feature card ─────────────────────────────────────────────────────────────

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

// ─── Features section ─────────────────────────────────────────────────────────

function Features() {
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

// ─── Footer ───────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="border-t border-slate-100 bg-white">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          {/* <div className="w-6 h-6 rounded-md bg-sky-500 flex items-center justify-center">
            <Shield className="w-3.5 h-3.5 text-white" />
          </div> */}
          <div className="w-6 h-6 rounded-lg bg-sky-500 flex items-center justify-center">
            <ActivityIcon className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-bold text-slate-900">Sensors2Care</span>
        </div>

        {/* Copyright */}
        <p className="text-xs text-slate-400 hidden sm:block">
          © 2025 Sensors2Care · Thesis project · Fontys ICT · Built for clinical IoT research
        </p>

        {/* GitHub link */}
        <a
          href="#"
          className="text-slate-400 hover:text-slate-700 transition-colors flex items-center gap-1 text-xs font-medium"
        >
          <ExternalLink className="w-4 h-4" />
          GitHub
        </a>
      </div>
    </footer>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function HomePage() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: "#F8FAFB" }}>
      <Navbar />
      <main>
        <Hero />
        <TrustBar />
        <Features />
      </main>
      <Footer />
    </div>
  );
}
