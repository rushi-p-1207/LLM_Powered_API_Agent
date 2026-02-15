import { serve } from "https://deno.land/std/http/server.ts";
import { formatSandboxOutput } from "./formatOutput.ts";

serve(async (req) => {
  if (req.method !== "POST") {
    return new Response("POST only", { status: 405 });
  }

  try {
    const { code } = await req.json();

    const response = await fetch("http://localhost:9000/execute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code }),
    });

    const result = await response.json();
    const cleanOutput = formatSandboxOutput(result);

    return new Response(cleanOutput, {
      headers: { "Content-Type": "text/plain" },
    });

    } catch (err) {
    console.error("Proxy Error:", err);
    return new Response(JSON.stringify({ error: String(err) }), { 
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }

}, { port: 8000 });
