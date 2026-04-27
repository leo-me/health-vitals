import { ArrowRight, Heart, Wind, Bell } from "lucide-react";
import { VitalCard } from "./VitalCard";

export function Hero() {
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