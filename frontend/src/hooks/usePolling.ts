import { useEffect, useRef } from "react";

/**
 * Polls ``callback`` on a fixed interval while ``active`` is true.
 * Task #33: used when WebSocket eval updates are unavailable (fallback).
 */
export function usePolling(callback: () => void | Promise<void>, intervalMs: number, active: boolean) {
  const cbRef = useRef(callback);
  cbRef.current = callback;

  useEffect(() => {
    if (!active || intervalMs <= 0) return;
    const id = window.setInterval(() => {
      void cbRef.current();
    }, intervalMs);
    return () => window.clearInterval(id);
  }, [active, intervalMs]);
}
