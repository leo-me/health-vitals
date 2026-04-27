import { ActivityIcon, ArrowRight } from "lucide-react";

export function Navbar() {
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