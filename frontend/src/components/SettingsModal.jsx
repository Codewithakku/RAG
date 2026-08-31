import React, { useState } from 'react';
import { X, Key, Cpu, Check, AlertCircle } from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  currentModel,
  currentApiKey,
  onSave,
}) {
  const [model, setModel] = useState(
    currentModel || 'gemini-3.7-flash'
  );

  const [apiKey, setApiKey] = useState(currentApiKey || '');
  const [savedMessage, setSavedMessage] = useState(false);
  const [error, setError] = useState('');

  // If modal is closed, don't render anything
  if (!isOpen) {
    return null;
  }

  // ---------------------------------------------------------
  // API Key Validation
  // ---------------------------------------------------------

  // Expected format:
  // AQ.xxxxxxxxxxxxxxxxxxxx
  const API_KEY_REGEX = /^AQ\.[A-Za-z0-9_-]{20,}$/;

  const isValidApiKeyFormat = (key) => {
    return API_KEY_REGEX.test(key.trim());
  };

  // ---------------------------------------------------------
  // API Key Change
  // ---------------------------------------------------------

  const handleApiKeyChange = (e) => {
    const value = e.target.value;

    setApiKey(value);

    // Clear error while user is typing
    if (value.trim() === '') {
      setError('');
    } else if (!isValidApiKeyFormat(value)) {
      setError(
        'Invalid API key format. Expected format: AQ.xxxxxxxxxxxxxxxx'
      );
    } else {
      setError('');
    }
  };

  // ---------------------------------------------------------
  // Save Settings
  // ---------------------------------------------------------

  const handleSave = (e) => {
    e.preventDefault();

    const trimmedKey = apiKey.trim();

    // Required check
    if (!trimmedKey) {
      setError('API key is required.');
      return;
    }

    // Format check
    if (!isValidApiKeyFormat(trimmedKey)) {
      setError(
        'Invalid API key format. Expected format: AQ.xxxxxxxxxxxxxxxx'
      );
      return;
    }

    // Send model + API key to parent
    onSave({
      model,
      apiKey: trimmedKey,
    });

    // Show success message
    setSavedMessage(true);

    // Close modal after 1 second
    setTimeout(() => {
      setSavedMessage(false);
      onClose();
    }, 1000);
  };

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[1000] p-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-gradient-to-b from-slate-800 to-slate-900 shadow-2xl shadow-black/50 p-7 flex flex-col gap-6">

        {/* Header */}
        <div className="flex justify-between items-center pb-5 border-b border-white/10">

          <h2 className="text-lg font-semibold flex items-center gap-2.5 text-white">

            <span className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-500/20 text-indigo-400">
              <Cpu size={18} />
            </span>

            RAG &amp; Model Configuration
          </h2>

          <button
            type="button"
            className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 hover:bg-white/15 text-slate-400 hover:text-white transition-colors"
            onClick={onClose}
          >
            <X size={16} />
          </button>

        </div>

        <form
          onSubmit={handleSave}
          className="flex flex-col gap-5"
        >

          {/* Gemini Model */}
          <div className="flex flex-col gap-2">

            <label className="text-xs uppercase tracking-wide text-slate-400 font-semibold">
              Google Gemini Model
            </label>

            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-slate-950 text-white border border-white/10 rounded-lg px-3.5 py-3 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/30 transition-colors cursor-pointer"
            >

              {/* Latest 3 Gemini models only */}

              <option value="gemini-3.7-flash">
                gemini-3.7-flash
              </option>

              <option value="gemini-3.6-flash">
                gemini-3.6-flash
              </option>

              <option value="gemini-3.5-flash">
                gemini-3.5-flash
              </option>

            </select>

          </div>

          {/* API Key */}
          <div className="flex flex-col gap-2">

            <label className="text-xs uppercase tracking-wide text-slate-400 font-semibold flex items-center gap-1.5">

              <Key
                size={13}
                className="text-cyan-400"
              />

              Google Gemini API Key

            </label>

            <input
              type="password"
              value={apiKey}
              onChange={handleApiKeyChange}
              placeholder="AQ.xxxxxxxxxxxxxxxxxxxxxxxx"
              className={`w-full bg-slate-950 text-white border rounded-lg px-3.5 py-3 text-sm outline-none font-mono placeholder:text-slate-600 focus:ring-2 transition-colors ${
                error
                  ? 'border-red-500/60 focus:border-red-500 focus:ring-red-500/30'
                  : 'border-white/10 focus:border-indigo-400 focus:ring-indigo-400/30'
              }`}
              required
            />

            {/* Error */}
            {error && (
              <div className="flex items-center gap-1.5 text-red-400 text-xs font-medium">

                <AlertCircle size={13} />

                {error}

              </div>
            )}

            <span className="text-xs text-slate-500 leading-relaxed">

              You can also set{' '}

              <code className="text-slate-400 bg-white/5 px-1 py-0.5 rounded">
                GOOGLE_API_KEY
              </code>{' '}

              in{' '}

              <code className="text-slate-400 bg-white/5 px-1 py-0.5 rounded">
                backend/.env
              </code>

            </span>

          </div>

          {/* Save Confirmation */}
          {savedMessage && (
            <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 rounded-lg px-3.5 py-2.5 text-emerald-400 text-sm font-medium">

              <Check size={16} />

              Configuration saved!

            </div>
          )}

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-2 border-t border-white/10 mt-1">

            <button
              type="button"
              className="px-4 py-2.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white text-sm font-medium transition-colors"
              onClick={onClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={!apiKey.trim() || !!error}
              className="px-5 py-2.5 rounded-lg bg-indigo-500 hover:bg-indigo-400 disabled:bg-slate-700 disabled:cursor-not-allowed disabled:shadow-none text-white text-sm font-semibold shadow-lg shadow-indigo-500/30 transition-colors"
            >
              Save Settings
            </button>

          </div>

        </form>

      </div>
    </div>
  );
}