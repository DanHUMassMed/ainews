const KNOWN_TEMPLATE_HEADINGS = [
  "Architectural & Benchmark Analysis",
  "Compute Economics & Scaling",
  "Enterprise Integration Takeaways",
  "Why It Matters",
  "Technical Deep-Dive",
  "Benchmark Results",
  "Key Findings",
  "Technical Overview",
  "Availability & Access",
];

/**
 * Cleans prose text (such as story summaries and "why it matters" sections)
 * by removing markdown heading markers and accidental template headers,
 * ensuring clean, readable prose without raw "#" symbols.
 * Any legitimate inline markdown formatting (bold, italic, links, code) is preserved.
 */
export function cleanProseMarkdown(text: string | null | undefined): string {
  if (!text) return "";
  let t = text;

  // 1. Remove known template headings (even if prefixed with ### or inline with prose)
  for (const h of KNOWN_TEMPLATE_HEADINGS) {
    const escaped = h.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(`(?:[\\s\\.]*)#{1,6}\\s*${escaped}[:\\s\\-]*(?:\\r?\\n)?`, "gi");
    t = t.replace(pattern, ". ");
  }

  // 2. Remove any line starting with markdown heading (# to ######)
  t = t.replace(/^\s*#{1,6}\s+.*$/gm, "");

  // 3. Remove any remaining inline #{1,6} heading indicators followed by title-like words
  t = t.replace(/#{1,6}\s+[A-Z][A-Za-z0-9\s&,:\-]{2,50}?(?=\s+[A-Z]|\n|$)/g, " ");
  // Remove dangling #{1,6} tokens
  t = t.replace(/#{1,6}\s*/g, "");

  // 4. Clean double periods or spaces before periods
  t = t.replace(/\s+\./g, ".");
  t = t.replace(/\.{2,}/g, ".");
  t = t.replace(/^[\s\.,\-:]+/, "");

  // Clean whitespace and join into paragraphs
  const paragraphs = t
    .split(/\n{2,}|\r\n\r\n/)
    .map((p) => p.replace(/\s+/g, " ").trim())
    .filter((p) => p.length > 0);

  return paragraphs.join("\n\n");
}

/**
 * Formats Markdown body content so that all headings (e.g. ### ...) are
 * properly separated by newlines as required by CommonMark, preventing headings
 * from being rendered as raw pound signs in inline text.
 */
export function formatBodyMarkdown(body: string | null | undefined): string {
  if (!body) return "";
  let t = body;

  // 1. Normalize known headings with double newlines
  for (const h of KNOWN_TEMPLATE_HEADINGS) {
    const escaped = h.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(`(?:[\\s\\.]*)#{1,6}\\s*${escaped}[:\\s\\-]*(?:\\r?\\n)?`, "gi");
    t = t.replace(pattern, `\n\n### ${h}\n\n`);
  }

  // 2. If any other #{1,6} appears after sentence punctuation inline, insert newline before it
  t = t.replace(/([.!?])\s*(#{1,6}\s+)/g, "$1\n\n$2");

  // 3. Ensure any line starting with #{1,6} has blank lines before and after it
  const lines = t.split(/\r?\n/);
  const formatted: string[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (/^#{1,6}\s+/.test(trimmed)) {
      formatted.push("");
      formatted.push(trimmed);
      formatted.push("");
    } else {
      formatted.push(line);
    }
  }

  t = formatted.join("\n");
  t = t.replace(/\n{3,}/g, "\n\n").trim();
  return t;
}
