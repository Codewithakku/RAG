import React, { useState } from 'react';
import { Send, Bot, BookOpen, Sparkles, ChevronDown, ChevronUp, Layers, HelpCircle, Loader2 } from 'lucide-react';

export default function QueryConsole({ onQuery, loading, hasKey }) {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(3);
  const [result, setResult] = useState(null);
  const [showSources, setShowSources] = useState(true);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setError(null);
    try {
      const res = await onQuery({ question, top_k: topK });
      setResult(res);
    } catch (err) {
      setError(err.message || 'Error generating answer from Gemini.');
    }
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/60 backdrop-blur-xl p-6 flex flex-col gap-5">

      {/* Header */}
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
            <Bot size={20} className="text-cyan-400" />
            RAG Query Console
          </h2>
          <p className="text-xs text-slate-400">
            Context-based Similarity Search + Google Gemini LLM
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">

          {/* Index Strategy Badge (Phase 4) */}
          {result?.index_strategy && (
            <div className="flex items-center gap-1.5 bg-black/30 border border-white/15 rounded-md px-2.5 py-1 text-xs text-slate-300">
              <Layers size={13} className="text-emerald-400" />
              Index: <span className="text-emerald-400 font-semibold">{result.index_strategy.index_strategy}</span>
              <span className="text-slate-500">({result.index_strategy.total_chunks} chunks)</span>
            </div>
          )}

          {/* Top K Selector */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Top K Chunks:</span>
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="bg-black/30 text-white border border-white/15 rounded-md px-2 py-1 text-sm outline-none"
            >
              <option value={1}>K = 1</option>
              <option value={3}>K = 3 (Default)</option>
              <option value={5}>K = 5</option>
            </select>
          </div>

        </div>
      </div>

      {/* Query Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div className="relative">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question based on your uploaded PDF documents..."
            rows={3}
            className="w-full bg-black/25 border border-white/15 rounded-lg p-3.5 pb-14 text-white text-[0.95rem] outline-none resize-none placeholder:text-slate-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="absolute right-3 bottom-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <Send size={15} />
                Ask Gemini
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error message */}
      {error && (
        <div className="px-4 py-3 bg-rose-950 border border-rose-800 rounded-lg text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Answer & Sources Display */}
      {result && (
        <div className="flex flex-col gap-4 mt-2">

          {/* Answer Card */}
          <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-5 relative">
            <div className="flex items-center gap-2 mb-3 text-indigo-400 font-semibold text-sm">
              <Sparkles size={18} />
              Gemini Answer (Context-Based)
            </div>

            <p className="leading-relaxed text-[0.95rem] whitespace-pre-wrap text-white">
              {result.answer}
            </p>
          </div>

          {/* Performance Timing (Phase 5) */}
          {result.performance && (
            <div className="text-xs text-slate-500 flex flex-wrap gap-3 px-1">
              <span>Retrieval: {result.performance.retrieval_sec}s</span>
              <span>Rerank: {result.performance.rerank_sec}s</span>
              <span>Gemini: {result.performance.gemini_sec}s</span>
              <span className="text-slate-300 font-semibold">
                Total: {result.performance.total_sec}s
              </span>
            </div>
          )}

          {/* Retrieved Context Sources (Top K = 3) */}
          {result.sources && result.sources.length > 0 && (
            <div className="flex flex-col gap-2.5">

              <button
                onClick={() => setShowSources(!showSources)}
                className="bg-transparent border-none text-slate-400 flex items-center gap-1.5 text-sm font-semibold cursor-pointer w-fit hover:text-slate-300 transition-colors"
              >
                <BookOpen size={15} className="text-cyan-400" />
                Retrieved Context Chunks ({result.sources.length} matching top k={topK})
                {showSources ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
              </button>

              {showSources && (
                <div className="flex flex-col gap-2.5">
                  {result.sources.map((src, idx) => (
                    <div
                      key={idx}
                      className="bg-black/25 border border-white/10 rounded-lg px-3.5 py-3 flex flex-col gap-1.5"
                    >
                      <div className="flex justify-between items-center text-xs text-cyan-400">
                        <span className="font-semibold">Chunk #{idx + 1} — {src.source_file}</span>
                        <span className="bg-cyan-950 px-2 py-0.5 rounded">{src.location}</span>
                      </div>
                      <p className="text-sm text-slate-400 font-mono leading-snug bg-black/30 px-2.5 py-2 rounded-md">
                        "{src.content}"
                      </p>
                    </div>
                  ))}
                </div>
              )}

            </div>
          )}

        </div>
      )}

    </div>
  );
}