"use client"

import { LoginModal } from "@/components/auth/LoginModal";
import { ArrowRight } from "lucide-react";
import { useState } from "react";


export function SignIn() {
  const [show, SetShow] = useState(false);

  return (
    <>
      <div className="flex items-center gap-3">
        <div
          className="text-sm text-slate-700 hover:text-slate-900 font-medium flex items-center gap-1 transition-colors"
          onClick={() => {
            console.log(222);
            SetShow(true);
          }}
        >
          Sign in <ArrowRight className="w-3.5 h-3.5" />
        </div>
        <a
          href="#"
          className="text-sm bg-slate-900 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-800 transition-colors flex items-center gap-1"
        >
          Get started <ArrowRight className="w-3.5 h-3.5" />
        </a>
      </div>
        
        {show && <LoginModal />}
    </>
    )
}