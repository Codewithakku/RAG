import React, { useState } from 'react';
import { UploadCloud, FileText, Trash2, RefreshCw, Layers, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function DocumentManager({ documents, onUpload, onUpdate, onDelete, loading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [updatingDocId, setUpdatingDocId] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      } else {
        setStatusMessage({ type: 'error', text: 'Only PDF files are allowed.' });
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      } else {
        setStatusMessage({ type: 'error', text: 'Only PDF files are allowed.' });
      }
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;
    setStatusMessage(null);
    try {
      if (updatingDocId) {
        await onUpdate(updatingDocId, selectedFile);
        setStatusMessage({ type: 'success', text: 'Document updated & re-indexed successfully!' });
      } else {
        await onUpload(selectedFile);
        setStatusMessage({ type: 'success', text: 'PDF loaded, split (500/50), & embedded in ChromaDB!' });
      }
      setSelectedFile(null);
      setUpdatingDocId(null);
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to process PDF.' });
    }
  };

  const startUpdate = (doc) => {
    setUpdatingDocId(doc.doc_id);
    setSelectedFile(null);
    setStatusMessage({ type: 'info', text: `Select a new PDF file to update document: ${doc.source_file}` });
  };

  const cancelUpdate = () => {
    setUpdatingDocId(null);
    setSelectedFile(null);
    setStatusMessage(null);
  };

  return (
    <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="var(--primary-accent)" />
            Document Storage Manager
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            PyPDFLoader • RecursiveCharacterTextSplitter (500 / 50)
          </p>
        </div>
        <div className="badge badge-info">
          {documents.length} PDF{documents.length !== 1 ? 's' : ''} Indexed
        </div>
      </div>

      {/* Status Alert Banner */}
      {statusMessage && (
        <div style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: statusMessage.type === 'error' ? 'rgba(244,63,94,0.15)' : statusMessage.type === 'success' ? 'rgba(16,185,129,0.15)' : 'rgba(6,182,212,0.15)',
          border: `1px solid ${statusMessage.type === 'error' ? 'rgba(244,63,94,0.3)' : statusMessage.type === 'success' ? 'rgba(16,185,129,0.3)' : 'rgba(6,182,212,0.3)'}`,
          color: statusMessage.type === 'error' ? 'var(--rose-accent)' : statusMessage.type === 'success' ? 'var(--emerald-accent)' : 'var(--cyan-accent)'
        }}>
          {statusMessage.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle size={16} />}
          <span style={{ flex: 1 }}>{statusMessage.text}</span>
          {updatingDocId && (
            <button className="btn-secondary" style={{ padding: '2px 8px', fontSize: '0.75rem' }} onClick={cancelUpdate}>
              Cancel Update
            </button>
          )}
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragActive ? 'var(--primary-accent)' : 'rgba(255,255,255,0.15)'}`,
          background: dragActive ? 'rgba(99,102,241,0.08)' : 'rgba(0,0,0,0.2)',
          borderRadius: 'var(--radius-md)',
          padding: '24px 16px',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
      >
        <input
          type="file"
          accept=".pdf"
          id="pdf-upload-input"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        
        <label htmlFor="pdf-upload-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <UploadCloud size={36} color={updatingDocId ? 'var(--secondary-accent)' : 'var(--primary-accent)'} />
          <div>
            <p style={{ fontWeight: 600, fontSize: '0.95rem' }}>
              {selectedFile ? selectedFile.name : updatingDocId ? 'Click to select replacement PDF' : 'Drop your PDF here, or browse'}
            </p>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Supports PDF files only • Chunks auto-generated at 500 size / 50 overlap
            </p>
          </div>
        </label>

        {selectedFile && (
          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '12px' }}>
            <button
              className="btn-primary"
              onClick={handleUploadSubmit}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                  Processing PDF...
                </>
              ) : updatingDocId ? (
                <>
                  <RefreshCw size={16} />
                  Confirm Update Document
                </>
              ) : (
                <>
                  <UploadCloud size={16} />
                  Add & Index Document
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Indexed Document List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Indexed Vector Documents ({documents.length})
        </h3>

        {documents.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', background: 'rgba(0,0,0,0.15)', borderRadius: 'var(--radius-md)', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No documents in vector storage. Upload a PDF to start similarity search.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '320px', overflowY: 'auto' }}>
            {documents.map((doc) => (
              <div
                key={doc.doc_id}
                style={{
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                  <FileText size={20} color="var(--cyan-accent)" style={{ flexShrink: 0 }} />
                  <div style={{ minWidth: 0 }}>
                    <p style={{ fontWeight: 600, fontSize: '0.88rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {doc.source_file}
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '2px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                        <Layers size={12} /> {doc.chunk_count} Chunks
                      </span>
                      <span>•</span>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>ID: {doc.doc_id.substring(0, 8)}...</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <button
                    className="btn-secondary"
                    style={{ padding: '5px 8px', fontSize: '0.75rem' }}
                    onClick={() => startUpdate(doc)}
                    title="Update PDF Document"
                  >
                    <RefreshCw size={13} />
                    Update
                  </button>
                  <button
                    className="btn-danger"
                    onClick={() => onDelete(doc.doc_id)}
                    title="Delete Document & Chunks"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
