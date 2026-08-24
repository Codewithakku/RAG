import React from 'react';
import { Cpu, Database, FileText, Settings, Sparkles } from 'lucide-react';

export default function Header({ health, onOpenSettings }) {
  return (
    <header className="glass-card" style={{ padding: '16px 24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Title & Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            padding: '10px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)'
          }}>
            <Sparkles size={24} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              RAG <span className="gradient-text">PDF Intelligence Studio</span>
            </h1>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              LangChain • ChromaDB • HuggingFace (all-MiniLM-L6-v2) • Gemini LLM
            </p>
          </div>
        </div>

        {/* Spec Status Pills & Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div className="badge badge-info">
            <Database size={13} />
            ChromaDB (Local)
          </div>
          <div className="badge badge-info">
            <FileText size={13} />
            500 / 50 Chunks
          </div>
          <div className="badge badge-info">
            <Cpu size={13} />
            {health?.default_gemini_model || 'gemini-2.0-flash'}
          </div>
          {health?.gemini_api_key_configured ? (
            <span className="badge badge-success">API Key Active</span>
          ) : (
            <span className="badge badge-warning">API Key Required</span>
          )}

          <button className="btn-secondary" onClick={onOpenSettings} title="Configure Gemini API Settings">
            <Settings size={16} />
            Settings
          </button>
        </div>

      </div>
    </header>
  );
}
