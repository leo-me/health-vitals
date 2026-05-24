"use client"

import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

export function DialogPortal({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);  // ← 初始 false

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);  // ← 只在客户端执行
  }, []);

  console.log(777);
    console.log('mounted: ', mounted);


  if (!mounted) return null;  // ← SSR 时直接返回 null，不碰 document
  console.log(888);
  return createPortal(children, document.body);
}