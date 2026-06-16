"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";
import { ToolCallCard } from "./ToolCallCard";

interface ChatPanelProps {
  messages: ChatMessage[];
}

export function ChatPanel({ messages }: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xs font-medium text-gray-400 uppercase tracking-[0.15em]">
          Agent Chat
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-gray-300 text-sm">
                Click &quot;Run Heapify&quot; to begin
              </p>
            </div>
          </div>
        )}

        {messages.map((msg) => {
          if (msg.type === "user") {
            return (
              <div key={msg.id} className="flex justify-end animate-fade-in">
                <div className="max-w-[75%] bg-red-500 rounded-2xl rounded-br-sm px-4 py-3">
                  <p className="text-[13px] leading-relaxed text-white">{msg.content}</p>
                </div>
              </div>
            );
          }

          if (msg.type === "tool_call" && msg.toolCall) {
            return (
              <div key={msg.id} className="animate-fade-in">
                <ToolCallCard toolCall={msg.toolCall} />
              </div>
            );
          }

          if (msg.type === "assistant") {
            return (
              <div key={msg.id} className="flex justify-start animate-fade-in">
                <div className="max-w-[75%] bg-gray-100 border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3">
                  <p className="text-[13px] leading-relaxed text-gray-700 whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            );
          }

          return null;
        })}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
