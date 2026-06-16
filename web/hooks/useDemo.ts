"use client";

import { useCallback, useRef, useState } from "react";
import type {
  ChatMessage,
  DemoStatus,
  MonitorEntry,
  ToolCallInfo,
} from "@/lib/types";

export function useDemo() {
  const [status, setStatus] = useState<DemoStatus>("idle");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [monitorEntries, setMonitorEntries] = useState<MonitorEntry[]>([]);
  const [hypothesis, setHypothesis] = useState<string>("");
  const abortRef = useRef<AbortController | null>(null);

  const addChat = useCallback((msg: ChatMessage) => {
    setChatMessages((prev) => [...prev, msg]);
  }, []);

  const updateToolCall = useCallback(
    (toolName: string, update: Partial<ToolCallInfo>) => {
      setChatMessages((prev) =>
        prev.map((m) => {
          if (
            m.type === "tool_call" &&
            m.toolCall?.toolName === toolName &&
            m.toolCall?.loading
          ) {
            return { ...m, toolCall: { ...m.toolCall, ...update } };
          }
          return m;
        })
      );
    },
    []
  );

  const addMonitor = useCallback((entry: MonitorEntry) => {
    setMonitorEntries((prev) => [...prev, entry]);
  }, []);

  const handleEvent = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (event: Record<string, any>) => {
      const { event_type, payload, id, created_at } = event;
      const ts: string = created_at ?? new Date().toISOString();
      const eid: string = id ?? crypto.randomUUID();

      switch (event_type) {
        case "run_start":
          setHypothesis(payload.hypothesis as string);
          addChat({ id: `user-${eid}`, type: "user", content: payload.task as string, timestamp: ts });
          addMonitor({ id: `mon-${eid}`, eventType: "run_start", label: "Run started", detail: payload.hypothesis as string, color: "blue", timestamp: ts });
          break;

        case "tool_call_start": {
          const toolName = payload.tool_name as string;
          const kind = payload.kind as "query" | "mutation";
          const args = (payload.args as Record<string, unknown>) || {};
          addChat({ id: `tc-${eid}`, type: "tool_call", content: "", toolCall: { toolName, kind, args, loading: true }, timestamp: ts });
          addMonitor({ id: `mon-${eid}`, eventType: "tool_call_start", label: `Intercepting ${toolName}...`, color: "yellow", timestamp: ts });
          break;
        }

        case "intercept": {
          const toolName = payload.tool_name as string;
          const mutated = payload.mutated as boolean;
          const description = payload.description as string;
          const result = payload.result as string;
          updateToolCall(toolName, { mutated, mutationDescription: description, result, loading: false });
          addMonitor({ id: `mon-${eid}`, eventType: "intercept", label: mutated ? `MUTATED: ${toolName}` : `Passed through: ${toolName}`, detail: mutated ? description : undefined, color: mutated ? "red" : "green", timestamp: ts });
          break;
        }

        case "evaluate_start":
          addMonitor({ id: `mon-${eid}`, eventType: "evaluate_start", label: "Evaluating run...", color: "yellow", timestamp: ts });
          break;

        case "evaluate_end":
          addMonitor({ id: `mon-${eid}`, eventType: "evaluate_end", label: "Evaluation complete", detail: payload.response as string, color: "blue", timestamp: ts });
          break;

        case "agent_response":
          addChat({ id: `asst-${eid}`, type: "assistant", content: payload.output as string, timestamp: ts });
          addMonitor({ id: `mon-${eid}`, eventType: "agent_response", label: "Agent responded", color: "blue", timestamp: ts });
          break;

        case "run_end": {
          const compromised = payload.compromised as boolean;
          setStatus("completed");
          addMonitor({ id: `mon-${eid}`, eventType: "run_end", label: compromised ? "COMPROMISED" : "SAFE", detail: payload.summary as string, color: compromised ? "red" : "green", timestamp: ts });
          break;
        }
      }
    },
    [addChat, addMonitor, updateToolCall]
  );

  const run = useCallback(
    async (selectedHypothesis: string) => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setChatMessages([]);
      setMonitorEntries([]);
      setHypothesis("");
      setStatus("running");

      try {
        const res = await fetch("/api/run-demo", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hypothesis: selectedHypothesis }),
          signal: controller.signal,
        });

        if (!res.ok || !res.body) { setStatus("error"); return; }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buf = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });
          const lines = buf.split("\n");
          buf = lines.pop() ?? "";
          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event = JSON.parse(line.slice(6));
              if (event.event_type === "stream_end") return;
              handleEvent(event);
            } catch { /* malformed */ }
          }
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== "AbortError") setStatus("error");
      }
    },
    [handleEvent]
  );

  const cleanup = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  return { status, chatMessages, monitorEntries, hypothesis, run, cleanup };
}
