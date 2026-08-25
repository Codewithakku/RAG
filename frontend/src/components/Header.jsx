import React from 'react';
import { Cpu, Database, FileText, Settings, Sparkles } from 'lucide-react';

export default function Header({ health, onOpenSettings }) {
  return (
    <header className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl px-6 py-4">
      <div className="flex justify-between items-center flex-wrap gap-4">

        {/* Title & Brand */}
        <div className="flex items-center gap-3.5">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-500 p-2.5 rounded-xl flex items-center justify-center shadow-[0_4px_12px_rgba(99,102,241,0.4)]">
            <Sparkles size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-[1.4rem] font-bold text-white">
              RAG <span className="gradient-text">PDF Intelligence Studio</span>
            </h1>
            <p className="text-[0.82rem] text-slate-400">
              LangChain • ChromaDB • HuggingFace (all-MiniLM-L6-v2) • Gemini LLM
            </p>
          </div>
        </div>

        {/* Spec Status Pills & Action */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
            <Database size={13} />
            ChromaDB (Local)
          </div>
          <div className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
            <FileText size={13} />
            500 / 50 Chunks
          </div>
          <div className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
            <Cpu size={13} />
            {health?.default_gemini_model || 'gemini-1.5-flash'}
          </div>
          {health?.gemini_api_key_configured ? (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              API Key Active
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30">
              API Key Required
            </span>
          )}

          <button
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
            onClick={onOpenSettings}
            title="Configure Gemini API Settings"
          >
            <Settings size={16} />
            Settings
          </button>
        </div>

      </div>
    </header>
  );
}