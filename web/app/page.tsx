"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useDemo } from "@/hooks/useDemo";
import { RunButton } from "@/components/RunButton";
import { ChatPanel } from "@/components/ChatPanel";
import { HeapifyMonitor } from "@/components/HeapifyMonitor";
import { HypothesisPicker } from "@/components/HypothesisPicker";

export default function Home() {
  const { status, chatMessages, monitorEntries, hypothesis, run, cleanup } =
    useDemo();
  const [selectedHypothesis, setSelectedHypothesis] = useState("");

  useEffect(() => {
    return () => cleanup();
  }, [cleanup]);

  const handleRun = () => run(selectedHypothesis);

  return (
    <div className="h-screen flex flex-col noise-bg bg-white">
      <header className="relative z-10 flex flex-col gap-4 px-8 py-5 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/logo.png"
              alt="heapify"
              width={40}
              height={40}
              className="rounded-full"
              priority
            />
            <span className="font-semibold text-gray-900 text-lg tracking-tight">heapify</span>
            <div className="h-4 w-px bg-gray-300 ml-2" />
            <span className="text-[11px] text-gray-400 tracking-wide hidden sm:inline">
              Adversarial fuzz-testing for AI agents
            </span>
          </div>

          <RunButton status={status} onClick={handleRun} />
        </div>

        <HypothesisPicker
          value={selectedHypothesis}
          onChange={setSelectedHypothesis}
          disabled={status === "running"}
        />
      </header>

      <main className="relative z-10 flex-1 flex overflow-hidden">
        <div className="w-[58%] border-r border-gray-200">
          <ChatPanel messages={chatMessages} />
        </div>

        <div className="w-[42%]">
          <HeapifyMonitor entries={monitorEntries} hypothesis={hypothesis} />
        </div>
      </main>

      <footer className="relative z-10 px-8 py-2.5 border-t border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className={`w-1.5 h-1.5 rounded-full transition-colors duration-500 ${
              status === "idle"
                ? "bg-gray-300"
                : status === "running"
                ? "bg-amber-500 animate-pulse"
                : status === "completed"
                ? "bg-emerald-500"
                : "bg-red-500"
            }`}
          />
          <span className="text-[11px] text-gray-400 tracking-wide">
            {status === "idle" && "Ready"}
            {status === "running" && "Agent under test..."}
            {status === "completed" && "Run complete"}
            {status === "error" && "Error occurred"}
          </span>
        </div>
        <span className="text-[11px] text-gray-300 tracking-wide">
          Powered by GitHub + Gemini
        </span>
      </footer>
    </div>
  );
}
