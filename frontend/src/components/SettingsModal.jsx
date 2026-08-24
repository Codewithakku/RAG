import React, { useState } from 'react';
import { X, Key, Cpu, Check } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, currentModel, currentApiKey, onSave }) {
  const [model, setModel] = useState(
    (currentModel === 'gemini-pro' || currentModel === 'gemini-2.0-flash') ? 'gemini-3.6-flash' : (currentModel || 'gemini-3.6-flash')
  );
  const [apiKey, setApiKey] = useState(currentApiKey || '');
  const [savedMessage, setSavedMessage] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    onSave({ model, apiKey });
    setSavedMessage(true);
    setTimeout(() => {
      setSavedMessage(false);
      onClose();
    }, 1000);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '16px'
    }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '480px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={20} color="var(--primary-accent)" />
            RAG & Model Configuration
          </h2>
          <button className="btn-secondary" style={{ padding: '4px 8px' }} onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Gemini Model Selection */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Google Gemini Model Name:
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              style={{
                background: 'rgba(0, 0, 0, 0.3)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-glow)',
                borderRadius: 'var(--radius-md)',
                padding: '10px',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            >
              <option value="gemini-3.6-flash">gemini-3.6-flash (Recommended)</option>
              <option value="gemini-1.5-flash">gemini-1.5-flash</option>
              <option value="gemini-1.5-pro">gemini-1.5-pro</option>
            </select>
          </div>

          {/* API Key Field */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Key size={14} color="var(--cyan-accent)" />
              Google Gemini API Key:
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIzaSy..."
              style={{
                background: 'rgba(0, 0, 0, 0.3)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-glow)',
                borderRadius: 'var(--radius-md)',
                padding: '10px',
                fontSize: '0.9rem',
                outline: 'none',
                fontFamily: 'var(--font-mono)'
              }}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              Note: You can also set GOOGLE_API_KEY in backend/.env file.
            </span>
          </div>

          {/* Save confirmation */}
          {savedMessage && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--emerald-accent)', fontSize: '0.85rem' }}>
              <Check size={16} /> Configuration saved!
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save Settings
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
