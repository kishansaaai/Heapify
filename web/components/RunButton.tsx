"use client";

import type { DemoStatus } from "@/lib/types";

interface RunButtonProps {
  status: DemoStatus;
  onClick: () => void;
}

export function RunButton({ status, onClick }: RunButtonProps) {
  const isRunning = status === "running";

  return (
    <button
      onClick={onClick}
      disabled={isRunning}
      className={`
        relative px-6 py-2.5 rounded-md text-[12px] font-medium tracking-[0.08em] uppercase
        transition-all duration-300 cursor-pointer
        ${
          isRunning
            ? "bg-gray-100 text-gray-400 border border-gray-200"
            : "bg-red-500 text-white border border-red-500 hover:bg-red-600 active:scale-[0.98]"
        }
        disabled:cursor-not-allowed
      `}
    >
      <span className="relative flex items-center gap-2">
        {isRunning && (
          <svg className="animate-spin h-3.5 w-3.5 text-gray-400" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {status === "idle" && "Run Heapify"}
        {status === "running" && "Running..."}
        {status === "completed" && "Run Again"}
        {status === "error" && "Retry"}
      </span>
    </button>
  );
}
