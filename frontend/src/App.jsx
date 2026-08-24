import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DocumentManager from './components/DocumentManager';
import QueryConsole from './components/QueryConsole';
import SettingsModal from './components/SettingsModal';

export default function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  const getInitialModel = () => {
    const saved = localStorage.getItem('gemini_model');
    if (!saved || saved === 'gemini-pro' || saved === 'gemini-2.0-flash') return 'gemini-3.6-flash';
    return saved;
  };

  const [userSettings, setUserSettings] = useState({
    model: getInitialModel(),
    apiKey: localStorage.getItem('gemini_api_key') || ''
  });

  // Helper for safe JSON parsing
  const parseJsonResponse = async (res) => {
    const text = await res.text();
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch (e) {
      if (!res.ok) {
        throw new Error(`Backend error (${res.status}): Please check if FastAPI server is running on port 8000.`);
      }
      throw new Error("Invalid response format received from server.");
    }
    if (!res.ok) {
      throw new Error(data.detail || `Server error (${res.status})`);
    }
    return data;
  };

  // Fetch backend health & documents list
  const fetchHealthAndDocs = async () => {
    try {
      const healthRes = await fetch('/api/health');
      if (healthRes.ok) {
        const hData = await parseJsonResponse(healthRes);
        setHealth(hData);
      }

      const docsRes = await fetch('/api/documents');
      if (docsRes.ok) {
        const dData = await parseJsonResponse(docsRes);
        setDocuments(dData.documents || []);
      }
    } catch (err) {
      console.error('Error connecting to RAG backend:', err);
    }
  };

  useEffect(() => {
    fetchHealthAndDocs();
  }, []);

  // Handle PDF Upload (Add Document)
  const handleUploadDocument = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await parseJsonResponse(res);
      await fetchHealthAndDocs();
      return data;
    } finally {
      setLoading(false);
    }
  };

  // Handle PDF Update (Update Document)
  const handleUpdateDocument = async (docId, file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`/api/documents/${docId}`, {
        method: 'PUT',
        body: formData,
      });

      const data = await parseJsonResponse(res);
      await fetchHealthAndDocs();
      return data;
    } finally {
      setLoading(false);
    }
  };

  // Handle PDF Delete (Delete Document)
  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document and all its chunks from vector storage?')) return;
    
    setLoading(true);
    try {
      const res = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE',
      });
      const data = await parseJsonResponse(res);
      await fetchHealthAndDocs();
    } catch (err) {
      alert(`Error deleting document: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle RAG Query
  const handleQuery = async ({ question, top_k }) => {
    setLoading(true);
    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          top_k,
          gemini_model: userSettings.model,
          api_key: userSettings.apiKey || undefined
        }),
      });

      const data = await parseJsonResponse(res);
      return data;
    } finally {
      setLoading(false);
    }
  };

  // Save Settings
  const handleSaveSettings = ({ model, apiKey }) => {
    setUserSettings({ model, apiKey });
    localStorage.setItem('gemini_model', model);
    if (apiKey) localStorage.setItem('gemini_api_key', apiKey);
    fetchHealthAndDocs();
  };

  return (
    <div className="app-container">
      
      {/* Header */}~
      <Header
        health={health}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Grid */}
      <main className="main-grid">
        
        {/* Left Column: Document Storage Manager (Add, Update, Delete, List) */}
        <DocumentManager
          documents={documents}
          onUpload={handleUploadDocument}
          onUpdate={handleUpdateDocument}
          onDelete={handleDeleteDocument}
          loading={loading}
        />

        {/* Right Column: Query & Answer Console (Similarity Search + Gemini) */}
        <QueryConsole
          onQuery={handleQuery}
          loading={loading}
          hasKey={health?.gemini_api_key_configured || Boolean(userSettings.apiKey)}
        />

      </main>

      {/* Footer */}
      <footer style={{ marginTop: 'auto', textAlign: 'center', padding: '16px', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
        RAG Implementation Plan • Built with LangChain, ChromaDB, Hugging Face, Google Gemini & React
      </footer>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentModel={userSettings.model}
        currentApiKey={userSettings.apiKey}
        onSave={handleSaveSettings}
      />

    </div>
  );
}
