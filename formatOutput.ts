export function formatSandboxOutput(raw: unknown): string {
  if (raw === null || raw === undefined || typeof raw !== "object") return "";

  const obj = raw as Record<string, unknown>;

  let text = "";

  if ("output" in obj && typeof obj.output === "string") {
    text = obj.output;
  } else if ("error" in obj && typeof obj.error === "string") {
    text = obj.error;
  }

  return text
    .replace(/\r\n/g, "\n")
    .replace(/\n\s*\n/g, "\n")
    .trim();
}
