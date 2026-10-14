// Placeholder shown in the dashboard cards before the first audit finishes.
export const EMPTY_JOB = {
  id: "",
  idle: true,
  status: "idle",
  agents: [],
  state: {
    url: "", readability: null, rivals: [], elements: [], answers: [], benchmark: [], timings: {},
    llm_tokens: { input: 0, output: 0 }, skeptic: {}, crawl: { bots: {} }, structured: { json_ld_types: [] },
  },
  report: {
    verdict: "", visibility_note: "Run an audit to compare your page with the pages that outrank it.",
    cant_read: [], cant_answer: [], top_fixes: [], survival: [], hidden: [], crawl: [], structured: [],
    benchmark: [], visibility: [],
  },
};
