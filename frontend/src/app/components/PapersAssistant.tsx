"use client";

import { useEffect, useRef, useState, type CSSProperties, type FormEvent, type KeyboardEvent } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Citation = { id: string; label: string; url: string };

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

type Paper = {
  title: string;
  arxivId: string;
  url: string;
};

type ApiPaper = {
  arxiv_id: string;
  title: string;
  pdf_filename: string;
  url: string;
};

type ApiSource = {
  label: string;
  file_name: string;
  score: number | null;
};

type ChatResponse = {
  answer: string;
  sources: ApiSource[];
};

const FALLBACK_PAPERS: Paper[] = [
  { title: "Attention Is All You Need", arxivId: "1706.03762", url: "https://arxiv.org/abs/1706.03762" },
  { title: "BERT: Pre-training of Deep Bidirectional Transformers", arxivId: "1810.04805", url: "https://arxiv.org/abs/1810.04805" },
  { title: "Language Models are Few-Shot Learners", arxivId: "2005.14165", url: "https://arxiv.org/abs/2005.14165" },
  { title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP", arxivId: "2005.11401", url: "https://arxiv.org/abs/2005.11401" },
  { title: "LoRA: Low-Rank Adaptation of Large Language Models", arxivId: "2106.09685", url: "https://arxiv.org/abs/2106.09685" },
  { title: "Chain-of-Thought Prompting Elicits Reasoning", arxivId: "2201.11903", url: "https://arxiv.org/abs/2201.11903" },
  { title: "Training Language Models to Follow Instructions", arxivId: "2203.02155", url: "https://arxiv.org/abs/2203.02155" },
  { title: "Constitutional AI: Harmlessness from AI Feedback", arxivId: "2212.08073", url: "https://arxiv.org/abs/2212.08073" },
  { title: "LLaMA: Open and Efficient Foundation Language Models", arxivId: "2302.13971", url: "https://arxiv.org/abs/2302.13971" },
  { title: "Toolformer: Language Models Can Teach Themselves to Use Tools", arxivId: "2302.04761", url: "https://arxiv.org/abs/2302.04761" },
  { title: "GPT-4 Technical Report", arxivId: "2303.08774", url: "https://arxiv.org/abs/2303.08774" },
  { title: "Visual Instruction Tuning", arxivId: "2304.08485", url: "https://arxiv.org/abs/2304.08485" },
  { title: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", arxivId: "2306.05685", url: "https://arxiv.org/abs/2306.05685" },
  { title: "QLoRA: Efficient Finetuning of Quantized LLMs", arxivId: "2305.14314", url: "https://arxiv.org/abs/2305.14314" },
  { title: "Direct Preference Optimization", arxivId: "2305.18290", url: "https://arxiv.org/abs/2305.18290" },
  { title: "Mamba: Linear-Time Sequence Modeling with Selective State Spaces", arxivId: "2312.00752", url: "https://arxiv.org/abs/2312.00752" },
  { title: "Mixtral of Experts", arxivId: "2401.04088", url: "https://arxiv.org/abs/2401.04088" },
  { title: "The Era of 1-bit LLMs", arxivId: "2402.17764", url: "https://arxiv.org/abs/2402.17764" },
  { title: "Scalable Extraction of Training Data from Production Language Models", arxivId: "2311.17035", url: "https://arxiv.org/abs/2311.17035" },
];

const SUGGESTIONS = [
  { id: "s1", label: "How do transformers handle long context?" },
  { id: "s2", label: "Compare RAG vs fine-tuning for domain Q&A" },
  { id: "s3", label: "What is LoRA and when should I use it?" },
];

function isApiPaper(value: unknown): value is ApiPaper {
  if (typeof value !== "object" || value === null) return false;
  const paper = value as Record<string, unknown>;
  return (
    typeof paper.arxiv_id === "string" &&
    typeof paper.title === "string" &&
    typeof paper.pdf_filename === "string" &&
    typeof paper.url === "string"
  );
}

function isApiSource(value: unknown): value is ApiSource {
  if (typeof value !== "object" || value === null) return false;
  const source = value as Record<string, unknown>;
  return (
    typeof source.label === "string" &&
    typeof source.file_name === "string" &&
    (source.score === null || source.score === undefined || typeof source.score === "number")
  );
}

function isChatResponse(value: unknown): value is ChatResponse {
  if (typeof value !== "object" || value === null) return false;
  const body = value as Record<string, unknown>;
  return typeof body.answer === "string" && Array.isArray(body.sources) && body.sources.every(isApiSource);
}

function mapApiPaper(paper: ApiPaper): Paper {
  return {
    title: paper.title,
    arxivId: paper.arxiv_id,
    url: paper.url.startsWith("http") ? paper.url : `https://arxiv.org/abs/${paper.arxiv_id}`,
  };
}

function citationFromSource(source: ApiSource, index: number): Citation {
  const arxivId = source.file_name.replace(/\.pdf$/i, "");
  return {
    id: `${source.label}-${arxivId}-${index}`,
    label: `arXiv:${arxivId}`,
    url: `https://arxiv.org/abs/${arxivId}`,
  };
}

function IconMenu({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="1.75">
      <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}

function IconSend({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

function IconArrow({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="1.75">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  );
}

function IconSpark({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="1.75">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3z"
      />
    </svg>
  );
}

export default function PapersAssistant() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [papers, setPapers] = useState<Paper[]>(FALLBACK_PAPERS);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadPapers() {
      try {
        const response = await fetch(`${API_BASE}/papers`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Papers request failed (${response.status})`);
        }
        const data: unknown = await response.json();
        if (!Array.isArray(data) || !data.every(isApiPaper)) {
          throw new Error("Unexpected papers payload");
        }
        setPapers(data.map(mapApiPaper));
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") return;
        setPapers(FALLBACK_PAPERS);
      }
    }

    void loadPapers();
    return () => controller.abort();
  }, []);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed (${response.status})`);
      }

      const data: unknown = await response.json();
      if (!isChatResponse(data)) {
        throw new Error("Unexpected chat payload");
      }

      const seen = new Set<string>();
      const citations: Citation[] = [];
      data.sources.forEach((source, index) => {
        const citation = citationFromSource(source, index);
        if (seen.has(citation.url)) return;
        seen.add(citation.url);
        citations.push(citation);
      });

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        citations: citations.length > 0 ? citations : undefined,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "I couldn't reach the papers backend. Make sure the FastAPI server is running at http://localhost:8000 and try again.",
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void sendMessage(input);
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendMessage(input);
    }
  }

  const isEmpty = messages.length === 0;
  const paperCount = papers.length;

  return (
    <div
      className="relative flex h-dvh w-full overflow-hidden text-white"
      style={
        {
          "--accent": "#34E0A1",
          "--mint": "#34E0A1",
          "--bg": "#000000",
          "--bg-elevated": "#0A0A0A",
          "--bg-panel": "#0F0F0F",
          "--text": "#F5F5F5",
          "--text-dim": "rgba(245,245,245,0.55)",
          background:
            "radial-gradient(1200px 600px at 15% -10%, rgba(52,224,161,0.12), transparent 55%), radial-gradient(900px 500px at 90% 110%, rgba(52,224,161,0.08), transparent 50%), #000000",
        } as CSSProperties
      }
    >
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-[2px] transition-opacity duration-300 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={[
          "fixed inset-y-0 left-0 z-40 flex flex-col overflow-hidden border-r border-white/[0.06] bg-[var(--bg-panel)]/95 backdrop-blur-md transition-[width,transform] duration-300 ease-out md:static md:translate-x-0",
          sidebarOpen
            ? "w-72 translate-x-0"
            : "w-0 -translate-x-full border-transparent md:w-0 md:translate-x-0",
        ].join(" ")}
      >
        <div
          className={[
            "flex h-full w-72 flex-col transition-opacity duration-300",
            sidebarOpen ? "opacity-100" : "pointer-events-none opacity-0",
          ].join(" ")}
        >
          <div className="flex items-center justify-between px-4 py-4">
            <h2 className="text-sm font-medium tracking-wide text-[var(--text)]">Papers</h2>
            <button
              type="button"
              className="rounded-lg p-1.5 text-[var(--text-dim)] transition hover:bg-white/5 hover:text-[var(--text)] md:hidden"
              onClick={() => setSidebarOpen(false)}
              aria-label="Close"
            >
              <span className="text-lg leading-none">×</span>
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto px-2 pb-4">
            <ul className="space-y-0.5">
              {papers.map((paper) => (
                <li key={paper.arxivId}>
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block rounded-xl px-3 py-2.5 no-underline transition hover:bg-white/[0.04]"
                  >
                    <p className="line-clamp-2 text-sm leading-snug text-[var(--text)]">{paper.title}</p>
                    <p className="mt-1 font-mono text-xs text-[var(--text-dim)]">arXiv:{paper.arxivId}</p>
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </aside>

      <div className="relative flex min-w-0 flex-1 flex-col">
        <header className="flex shrink-0 items-center gap-3 border-b border-white/[0.06] px-4 py-3">
          <button
            type="button"
            onClick={() => setSidebarOpen((v) => !v)}
            className="rounded-lg p-2 text-[var(--text-dim)] transition hover:bg-white/5 hover:text-[var(--text)]"
            aria-label="Toggle papers sidebar"
            aria-expanded={sidebarOpen}
          >
            <IconMenu />
          </button>
          <div>
            <p className="text-sm font-medium text-[var(--text)]">Papers Assistant</p>
            <p className="text-xs text-[var(--text-dim)]">{paperCount} curated AI/ML papers</p>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          {isEmpty ? (
            <div className="flex h-full flex-col items-center justify-center px-4 pb-8">
              <div className="relative mb-6">
                <div
                  className="absolute inset-0 rounded-full bg-[var(--accent)] opacity-20 blur-2xl"
                  aria-hidden="true"
                />
                <div className="relative flex h-16 w-16 items-center justify-center rounded-full border border-[var(--accent)]/25 bg-[var(--bg-elevated)] text-[var(--accent)] shadow-[0_0_28px_rgba(52,224,161,0.22)]">
                  <IconSpark />
                </div>
              </div>

              <h1 className="mb-2 text-2xl font-semibold tracking-tight text-[var(--text)] sm:text-3xl">
                Ask Your Papers
              </h1>
              <p className="mb-10 max-w-md text-center text-sm text-[var(--text-dim)] sm:text-base">
                Grounded answers with citations, from {paperCount} curated AI/ML papers
              </p>

              <div className="flex w-full max-w-md flex-col gap-2.5">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => void sendMessage(s.label)}
                    className="group flex w-full items-center gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.03] px-4 py-3.5 text-left transition duration-200 hover:border-[var(--accent)]/30 hover:bg-white/[0.05]"
                  >
                    <span className="flex-1 text-sm text-[var(--text)]">{s.label}</span>
                    <IconArrow className="h-4 w-4 shrink-0 text-[var(--text-dim)] transition group-hover:text-[var(--accent)]" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-6">
              {messages.map((msg) =>
                msg.role === "user" ? (
                  <div key={msg.id} className="flex justify-end">
                    <div className="max-w-[85%] rounded-2xl rounded-br-md bg-gradient-to-br from-[#34E0A1] to-[#1FAE78] px-4 py-2.5 text-sm leading-relaxed text-black shadow-[0_0_20px_rgba(52,224,161,0.18)]">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div key={msg.id} className="flex flex-col gap-3">
                    <p className="max-w-[90%] text-sm leading-relaxed text-[var(--text)] sm:text-[15px]">
                      {msg.content}
                    </p>
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {msg.citations.map((c) => (
                          <a
                            key={c.id}
                            href={c.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center rounded-full border border-[var(--accent)]/20 bg-[var(--accent)]/10 px-2.5 py-0.5 font-mono text-[11px] text-[var(--accent)] no-underline transition hover:bg-[var(--accent)]/15"
                          >
                            {c.label}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                )
              )}

              {loading && (
                <div className="flex items-center gap-1.5 text-[var(--text-dim)]">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--accent)]" />
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--accent)] [animation-delay:150ms]" />
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--accent)] [animation-delay:300ms]" />
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </main>

        <div className="shrink-0 px-4 pb-5 pt-2">
          <form
            onSubmit={onSubmit}
            className="mx-auto flex w-full max-w-2xl items-center gap-2 rounded-full border border-white/[0.08] bg-[var(--bg-elevated)]/90 px-2 py-1.5 backdrop-blur-sm transition focus-within:border-[var(--accent)]/35 focus-within:shadow-[0_0_24px_rgba(52,224,161,0.12)]"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Type message..."
              disabled={loading}
              className="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-sm text-[var(--text)] outline-none placeholder:text-[var(--text-dim)] disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              aria-label="Send message"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#34E0A1] to-[#1FAE78] text-black shadow-[0_0_18px_rgba(52,224,161,0.35)] transition enabled:hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
            >
              <IconSend />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
