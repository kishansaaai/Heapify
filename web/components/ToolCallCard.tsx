"use client";

import { useState } from "react";
import type { ToolCallInfo } from "@/lib/types";

interface ToolCallCardProps {
  toolCall: ToolCallInfo;
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [expanded, setExpanded] = useState(false);
  const { toolName, kind, args, result, mutated, mutationDescription, loading } = toolCall;

  return (
    <div
      className={`
        rounded-lg border transition-all duration-300 overflow-hidden
        ${mutated
          ? "border-red-200 bg-red-50"
          : "border-gray-200 bg-gray-50"
        }
      `}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center gap-3 text-left cursor-pointer hover:bg-black/[0.02] transition-colors"
      >
        <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${loading ? "animate-pulse bg-amber-500" : mutated ? "bg-red-500" : "bg-emerald-500"}`} />

        <span className="text-[13px] font-mono text-gray-700 flex-1">
          {toolName}
        </span>

        <span
          className={`
            text-[9px] font-medium uppercase tracking-[0.1em] px-2 py-0.5 rounded-full
            ${kind === "mutation"
              ? "bg-amber-100 text-amber-700"
              : "bg-gray-200 text-gray-500"
            }
          `}
        >
          {kind}
        </span>

        {mutated && (
          <span className="text-[9px] font-medium uppercase tracking-[0.1em] px-2 py-0.5 rounded-full bg-red-100 text-red-600">
            mutated
          </span>
        )}

        {loading && (
          <span className="text-[10px] text-gray-400 italic">intercepting...</span>
        )}

        <svg
          className={`w-3.5 h-3.5 text-gray-300 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="px-4 pb-3 space-y-3 border-t border-gray-200">
          <div className="pt-3">
            <p className="text-[9px] uppercase tracking-[0.15em] text-gray-400 mb-1.5">Arguments</p>
            <pre className="text-xs text-gray-600 font-mono bg-white border border-gray-200 rounded-md p-2.5 overflow-x-auto">
              {JSON.stringify(args, null, 2)}
            </pre>
          </div>

          {result != null && (
            <div>
              <p className="text-[9px] uppercase tracking-[0.15em] text-gray-400 mb-1.5">Result</p>
              <pre className="text-xs text-gray-600 font-mono bg-white border border-gray-200 rounded-md p-2.5 overflow-x-auto max-h-48 overflow-y-auto">
                {(() => {
                  if (typeof result !== "string") {
                    return JSON.stringify(result, null, 2);
                  }
                  try {
                    return JSON.stringify(JSON.parse(result), null, 2);
                  } catch {
                    return result;
                  }
                })()}
              </pre>
            </div>
          )}

          {mutated && mutationDescription && (
            <div className="rounded-md bg-red-50 border border-red-200 p-2.5">
              <p className="text-[9px] uppercase tracking-[0.15em] text-red-500 mb-1.5">Mutation</p>
              <p className="text-xs text-red-700 leading-relaxed">{mutationDescription}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
