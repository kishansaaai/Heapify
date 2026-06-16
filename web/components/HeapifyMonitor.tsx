"use client";

import { useEffect, useRef } from "react";
import type { MonitorEntry } from "@/lib/types";

interface HeapifyMonitorProps {
  entries: MonitorEntry[];
  hypothesis: string;
}

const colorMap = {
  blue: { dot: "bg-blue-500", text: "text-blue-600" },
  yellow: { dot: "bg-amber-500 animate-pulse", text: "text-amber-600" },
  green: { dot: "bg-emerald-500", text: "text-emerald-600" },
  red: { dot: "bg-red-500", text: "text-red-600" },
};

export function HeapifyMonitor({ entries, hypothesis }: HeapifyMonitorProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries]);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xs font-medium text-gray-400 uppercase tracking-[0.15em]">
          Monitor
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5">
        {hypothesis && (
          <div className="mb-6 rounded-lg bg-white border border-gray-200 p-4">
            <p className="text-[9px] uppercase tracking-[0.15em] text-gray-400 mb-2">Hypothesis</p>
            <p className="text-[12px] text-gray-600 leading-relaxed">{hypothesis}</p>
          </div>
        )}

        {entries.length === 0 && !hypothesis && (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-300 text-sm">Waiting for events...</p>
          </div>
        )}

        <div className="space-y-0">
          {entries.map((entry, i) => {
            const colors = colorMap[entry.color];
            const isLast = i === entries.length - 1;
            const isRunEnd = entry.eventType === "run_end";
            const isCompromised = isRunEnd && entry.label === "COMPROMISED";

            return (
              <div key={entry.id} className="flex gap-3.5 animate-fade-in">
                <div className="flex flex-col items-center">
                  <div
                    className={`
                      ${isRunEnd ? "w-3 h-3" : "w-2 h-2"} rounded-full shrink-0 mt-1.5
                      ${colors.dot}
                      ${isCompromised ? "shadow-[0_0_8px_rgba(220,38,38,0.4)]" : ""}
                    `}
                  />
                  {!isLast && (
                    <div className="w-px flex-1 min-h-[20px] bg-gray-200" />
                  )}
                </div>

                <div className="pb-4">
                  <p className={`text-[12px] font-medium ${colors.text}`}>
                    {entry.label}
                  </p>
                  {entry.detail && (
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
                      {entry.detail}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
