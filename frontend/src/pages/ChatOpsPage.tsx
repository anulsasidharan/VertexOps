import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { Bot, Send, User } from "lucide-react";
import { runQuery } from "@/api/query";
import { fetchIndexes } from "@/api/indexes";
import type { IndexDto, QueryResponseDto } from "@/api/types";
import { useAuthSession } from "@/context/AuthSessionContext";

type Message = {
  id: string; role: "user" | "ai";
  text?: string; result?: QueryResponseDto; loading?: boolean;
};

const QUICK_PROMPTS = [
  "Why is production GKE cluster latency high?",
  "Show me resources with CPU > 80%",
  "What incidents occurred in the last 24 hours?",
  "Which AWS resources are idle and cost the most?",
];

export function ChatOpsPage() {
  const { getAuthHeaders } = useAuthSession();
  const [messages, setMessages] = useState<Message[]>([
    { id: "intro", role: "ai", text: "Hi! I'm your AI infrastructure assistant. Ask me anything about your multi-cloud environment — incidents, resources, costs, compliance, or performance." },
  ]);
  const [input, setInput] = useState("");
  const [indexes, setIndexes] = useState<IndexDto[]>([]);
  const [indexId, setIndexId] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchIndexes(getAuthHeaders())
      .then((d) => {
        setIndexes(d.items);
        if (d.items[0]) setIndexId(d.items[0].id);
      })
      .catch(() => {});
  }, [getAuthHeaders]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async (question: string) => {
    if (!question.trim() || loading) return;
    const id = Date.now().toString();
    setMessages((m) => [...m, { id, role: "user", text: question }, { id: id + "r", role: "ai", loading: true }]);
    setInput("");
    setLoading(true);
    try {
      const result = await runQuery(getAuthHeaders(), { question: question.trim(), index_id: indexId, top_k: 5 });
      setMessages((m) =>
        m.map((msg) => msg.id === id + "r" ? { ...msg, loading: false, result, text: result.answer } : msg)
      );
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : "Query failed";
      setMessages((m) =>
        m.map((msg) => msg.id === id + "r" ? { ...msg, loading: false, text: `Error: ${errMsg}` } : msg)
      );
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders, indexId, loading]);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void send(input);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] min-h-0">
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div>
          <h1 className="text-xl font-semibold flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" /> ChatOps AI
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">RAG-powered · searches logs, metrics, docs &amp; incident history</p>
        </div>
        {indexes.length > 0 && (
          <select
            value={indexId}
            onChange={(e) => setIndexId(e.target.value)}
            className="rounded border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-300"
          >
            {indexes.map((idx) => (
              <option key={idx.id} value={idx.id}>{idx.name}</option>
            ))}
          </select>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 min-h-0">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "ai" && (
              <div className="w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-600/40 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-indigo-400" />
              </div>
            )}
            <div className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-indigo-600 text-white"
                : "bg-slate-900 border border-slate-800 text-slate-300"
            }`}>
              {msg.loading ? (
                <div className="flex gap-1 py-1">
                  {[0, 1, 2].map((i) => (
                    <span key={i} className="w-2 h-2 rounded-full bg-slate-500 animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </div>
              ) : (
                <>
                  <p>{msg.text}</p>
                  {msg.result && msg.result.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">Sources</div>
                      <div className="space-y-2">
                        {msg.result.sources.slice(0, 3).map((src) => (
                          <div key={src.chunk_id} className="bg-slate-800 rounded-lg p-2.5 text-xs">
                            <div className="flex justify-between mb-1">
                              <span className="text-indigo-400 font-medium">Doc {src.document_id.slice(0, 8)}…</span>
                              <span className="text-slate-500">score: {src.score.toFixed(2)}</span>
                            </div>
                            <p className="text-slate-400 leading-snug line-clamp-2">{src.text}</p>
                          </div>
                        ))}
                      </div>
                      <div className="flex flex-wrap gap-2 mt-2.5 text-xs text-slate-500">
                        <span>Model: {msg.result.model}</span>
                        <span>·</span>
                        <span>Latency: {msg.result.latency_ms}ms</span>
                        <span>·</span>
                        <span>Tokens: {msg.result.prompt_tokens + msg.result.completion_tokens}</span>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
            {msg.role === "user" && (
              <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
                <User className="w-4 h-4 text-slate-400" />
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Quick prompts */}
      {messages.length <= 2 && (
        <div className="flex flex-wrap gap-2 py-3 flex-shrink-0">
          {QUICK_PROMPTS.map((q) => (
            <button key={q} onClick={() => void send(q)}
              className="rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors">
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={onSubmit} className="flex gap-2 pt-3 flex-shrink-0 border-t border-slate-800">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything about your infrastructure…"
          className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}
          className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-40 flex items-center gap-1.5 transition-colors">
          <Send className="w-4 h-4" />
        </button>
      </form>
      {!indexId && (
        <p className="text-xs text-amber-400 mt-1.5 flex-shrink-0">
          ⚠ No index selected — create an index under Indexes first.
        </p>
      )}
    </div>
  );
}
