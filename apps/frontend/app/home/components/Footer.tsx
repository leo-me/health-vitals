import { ActivityIcon, ExternalLink } from "lucide-react";

export function Footer() {
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