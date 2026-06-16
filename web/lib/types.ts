export type EventType =
  | "run_start"
  | "tool_call_start"
  | "intercept"
  | "tool_call_end"
  | "agent_response"
  | "evaluate_start"
  | "evaluate_end"
  | "run_end";

export interface DemoEvent {
  id: string;
  run_id: string;
  seq: number;
  event_type: EventType;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  type: "user" | "assistant" | "tool_call";
  content: string;
  toolCall?: ToolCallInfo;
  timestamp: string;
}

export interface ToolCallInfo {
  toolName: string;
  kind: "query" | "mutation";
  args: Record<string, unknown>;
  result?: unknown;
  mutated?: boolean;
  mutationDescription?: string;
  loading: boolean;
}

export interface MonitorEntry {
  id: string;
  eventType: EventType;
  label: string;
  detail?: string;
  color: "blue" | "yellow" | "green" | "red";
  timestamp: string;
}

export type DemoStatus = "idle" | "running" | "completed" | "error";
