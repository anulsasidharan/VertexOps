"use client";
import { useEffect, useRef } from "react";
import { X } from "lucide-react";

type Props = {
  onClose: () => void;
};

export function DemoModal({ onClose }: Props) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.body.style.overflow = "hidden";
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);

    const msgHandler = (e: MessageEvent) => {
      if (e.data === "start-trial") {
        onClose();
        document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth" });
      }
    };
    window.addEventListener("message", msgHandler);

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handler);
      window.removeEventListener("message", msgHandler);
    };
  }, [onClose]);

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8"
      style={{ background: "rgba(0,0,0,0.85)" }}
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <div
        className="relative w-full flex flex-col rounded-2xl overflow-hidden shadow-2xl"
        style={{ maxWidth: 1100, height: "min(88vh, 700px)" }}
      >
        {/* Header bar */}
        <div className="flex items-center justify-between px-5 py-3 bg-gray-950 border-b border-gray-800 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            <span className="text-sm font-semibold text-white">VertexOps — Interactive Product Demo</span>
          </div>
          <button
            onClick={onClose}
            aria-label="Close demo"
            className="w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Demo iframe */}
        <iframe
          src="/demo/index.html"
          title="VertexOps Interactive Product Demo"
          className="flex-1 w-full border-0 block"
          allow="fullscreen"
          loading="lazy"
        />
      </div>
    </div>
  );
}
