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
    <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bot size={20} color="var(--cyan-accent)" />
            RAG Query Console
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Context-based Similarity Search + Google Gemini LLM
          </p>
        </div>

        {/* Top K Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Top K Chunks:</span>
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            style={{
              background: 'rgba(0,0,0,0.3)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-glow)',
              borderRadius: 'var(--radius-sm)',
              padding: '4px 8px',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          >
            <option value={1}>K = 1</option>
            <option value={3}>K = 3 (Default)</option>
            <option value={5}>K = 5</option>
          </select>
        </div>
      </div>

      {/* Query Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ position: 'relative' }}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question based on your uploaded PDF documents..."
            rows={3}
            style={{
              width: '100%',
              background: 'rgba(0, 0, 0, 0.25)',
              border: '1px solid var(--border-glow)',
              borderRadius: 'var(--radius-md)',
              padding: '14px',
              color: 'var(--text-main)',
              fontSize: '0.95rem',
              fontFamily: 'var(--font-body)',
              outline: 'none',
              resize: 'none'
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !question.trim()}
            style={{
              position: 'absolute',
              right: '12px',
              bottom: '12px',
              padding: '8px 16px',
              fontSize: '0.85rem'
            }}
          >
            {loading ? (
              <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
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
        <div style={{
          padding: '12px 16px',
          background: 'rgba(244, 63, 94, 0.15)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--rose-accent)',
          fontSize: '0.85rem'
        }}>
          {error}
        </div>
      )}

      {/* Answer & Sources Display */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '8px' }}>
          
          {/* Answer Card */}
          <div style={{
            background: 'rgba(99, 102, 241, 0.06)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: 'var(--radius-md)',
            padding: '20px',
            position: 'relative'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: 'var(--primary-accent)', fontWeight: 600, fontSize: '0.9rem' }}>
              <Sparkles size={18} />
              Gemini Answer (Context-Based)
            </div>

            <p style={{ lineHeight: '1.6', fontSize: '0.95rem', whiteSpace: 'pre-wrap', color: 'var(--text-main)' }}>
              {result.answer}
            </p>
          </div>

          {/* Retrieved Context Sources (Top K = 3) */}
          {result.sources && result.sources.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              
              <button
                onClick={() => setShowSources(!showSources)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  width: 'fit-content'
                }}
              >
                <BookOpen size={15} color="var(--cyan-accent)" />
                Retrieved Context Chunks ({result.sources.length} matching top k={topK})
                {showSources ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
              </button>

              {showSources && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {result.sources.map((src, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'rgba(0, 0, 0, 0.25)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: 'var(--radius-md)',
                        padding: '12px 14px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: 'var(--cyan-accent)' }}>
                        <span style={{ fontWeight: 600 }}>Chunk #{idx + 1} — {src.source_file}</span>
                        <span style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>Page {src.page}</span>
                      </div>
                      <p style={{ fontSize: '0.83rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', lineHeight: '1.4', background: 'rgba(0,0,0,0.3)', padding: '8px 10px', borderRadius: '6px' }}>
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
