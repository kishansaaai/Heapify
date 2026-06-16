import { spawn } from "child_process";
import path from "path";

export async function POST(req: Request) {
  const { hypothesis } = await req.json();
  const runId = crypto.randomUUID();

  const scriptPath = path.join(process.cwd(), "python", "run_demo.py");
  const env: NodeJS.ProcessEnv = {
    ...process.env,
    RUN_ID: runId,
    HYPOTHESIS: hypothesis || "",
  };

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      const proc = spawn("python", [scriptPath], { env });

      let buffer = "";

      const processChunk = (chunk: string) => {
        buffer += chunk;
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("{")) continue;
          try {
            const event = JSON.parse(trimmed);
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify(event)}\n\n`)
            );
          } catch {
            // non-JSON line, skip
          }
        }
      };

      proc.stdout.on("data", (data: Buffer) => processChunk(data.toString()));

      proc.stderr.on("data", (data: Buffer) => {
        console.error("[run-demo stderr]", data.toString());
      });

      proc.on("close", () => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ event_type: "stream_end" })}\n\n`)
        );
        controller.close();
      });

      proc.on("error", (err: Error) => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ event_type: "stream_end", error: err.message })}\n\n`)
        );
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
