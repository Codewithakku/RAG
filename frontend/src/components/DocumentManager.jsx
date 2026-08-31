import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  Trash2,
  RefreshCw,
  Layers,
  CheckCircle,
  AlertCircle,
  Loader2,
} from 'lucide-react';


// ============================================================
// Supported File Types
// ============================================================

const ALLOWED_EXTENSIONS = [
  '.pdf',
  '.txt',
  '.md',
  '.csv',
  '.xls',
  '.xlsx',
];

const ACCEPTED_FILES = ALLOWED_EXTENSIONS.join(',');


// ============================================================
// Component
// ============================================================

export default function DocumentManager({
  documents,
  onUpload,
  onUpdate,
  onDelete,
  loading,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [updatingDocId, setUpdatingDocId] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);


  // ==========================================================
  // Handle File Selection
  // ==========================================================

  const handleFileChange = (e) => {

    if (!e.target.files || !e.target.files[0]) {
      return;
    }

    const file = e.target.files[0];

    const fileName = file.name.toLowerCase();

    const isAllowed = ALLOWED_EXTENSIONS.some(
      (extension) => fileName.endsWith(extension)
    );

    if (!isAllowed) {

      setSelectedFile(null);

      setStatusMessage({
        type: 'error',
        text:
          'Unsupported file type. Please select PDF, TXT, MD, CSV, XLS, or XLSX.',
      });

      return;
    }

    setSelectedFile(file);

    setStatusMessage({
      type: 'info',
      text: `${file.name} selected successfully.`,
    });
  };


  // ==========================================================
  // Upload / Update
  // ==========================================================

  const handleUploadSubmit = async () => {

    if (!selectedFile) {
      return;
    }

    setStatusMessage(null);

    try {

      if (updatingDocId) {

        await onUpdate(
          updatingDocId,
          selectedFile
        );

        setStatusMessage({
          type: 'success',
          text:
            'Document updated & re-indexed successfully!',
        });

      } else {

        await onUpload(selectedFile);

        setStatusMessage({
          type: 'success',
          text:
            `${selectedFile.name} loaded, chunked, embedded & stored in ChromaDB!`,
        });
      }

      setSelectedFile(null);
      setUpdatingDocId(null);

    } catch (err) {

      setStatusMessage({
        type: 'error',
        text:
          err.message ||
          'Failed to process document.',
      });
    }
  };


  // ==========================================================
  // Start Update
  // ==========================================================

  const startUpdate = (doc) => {

    setUpdatingDocId(doc.doc_id);

    setSelectedFile(null);

    setStatusMessage({
      type: 'info',
      text:
        `Select a new document to replace: ${doc.source_file}`,
    });
  };


  // ==========================================================
  // Cancel Update
  // ==========================================================

  const cancelUpdate = () => {

    setUpdatingDocId(null);

    setSelectedFile(null);

    setStatusMessage(null);
  };


  // ==========================================================
  // Status Styles
  // ==========================================================

  const statusStyles = {

    error:
      'bg-rose-500/15 border-rose-500/30 text-rose-400',

    success:
      'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',

    info:
      'bg-cyan-500/15 border-cyan-500/30 text-cyan-400',
  };


  // ==========================================================
  // Get File Extension
  // ==========================================================

  const getFileExtension = (filename) => {

    const parts = filename.split('.');

    if (parts.length < 2) {
      return '';
    }

    return parts.pop().toUpperCase();
  };


  // ==========================================================
  // Render
  // ==========================================================

  return (

    <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 flex flex-col gap-5">


      {/* ======================================================
          Header
      ====================================================== */}

      <div className="flex items-center justify-between">

        <div>

          <h2 className="text-lg font-semibold flex items-center gap-2 text-white">

            <FileText
              size={18}
              className="text-indigo-400"
            />

            Document Storage Manager

          </h2>

          <p className="text-xs text-slate-400">

            Multi-format Loader • RecursiveCharacterTextSplitter
            (500 / 50)

          </p>

        </div>


        <div className="text-xs font-medium px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 whitespace-nowrap">

          {documents.length}{' '}
          Document
          {documents.length !== 1 ? 's' : ''}{' '}
          Indexed

        </div>

      </div>


      {/* ======================================================
          Status Alert
      ====================================================== */}

      {statusMessage && (

        <div
          className={`px-4 py-3 rounded-lg text-sm flex items-center gap-2.5 border ${
            statusStyles[statusMessage.type] ||
            statusStyles.info
          }`}
        >

          {statusMessage.type === 'error' ? (

            <AlertCircle size={16} />

          ) : (

            <CheckCircle size={16} />

          )}

          <span className="flex-1">

            {statusMessage.text}

          </span>


          {updatingDocId && (

            <button
              className="px-2 py-0.5 text-xs rounded-md bg-white/10 hover:bg-white/20 transition-colors"
              onClick={cancelUpdate}
            >
              Cancel Update
            </button>

          )}

        </div>

      )}


      {/* ======================================================
          File Select Zone
      ====================================================== */}

      <div className="rounded-lg border-2 border-dashed border-white/15 bg-black/20 p-6 text-center">


        <input
          type="file"
          accept={ACCEPTED_FILES}
          id="document-upload-input"
          className="hidden"
          onChange={handleFileChange}
        />


        <label
          htmlFor="document-upload-input"
          className="cursor-pointer flex flex-col items-center gap-2"
        >

          <UploadCloud
            size={36}
            className={
              updatingDocId
                ? 'text-purple-400'
                : 'text-indigo-400'
            }
          />


          <div>

            <p className="font-semibold text-sm text-white">

              {selectedFile

                ? selectedFile.name

                : updatingDocId

                ? 'Click to select replacement document'

                : 'Click to browse and select a document'}

            </p>


            <p className="text-[0.78rem] text-slate-400 mt-1">

              Supports PDF, TXT, MD, CSV, XLS & XLSX

            </p>

          </div>

        </label>


        {/* ====================================================
            Selected File Information
        ==================================================== */}

        {selectedFile && (

          <div className="mt-4 flex flex-col items-center gap-3">

            <div className="text-xs text-slate-400">

              File Type:{' '}

              <span className="text-cyan-400 font-semibold">

                {getFileExtension(
                  selectedFile.name
                )}

              </span>

            </div>


            <button
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
              onClick={handleUploadSubmit}
              disabled={loading}
            >

              {loading ? (

                <>

                  <Loader2
                    size={16}
                    className="animate-spin"
                  />

                  Processing...

                </>

              ) : updatingDocId ? (

                <>

                  <RefreshCw size={16} />

                  Confirm Update Document

                </>

              ) : (

                <>

                  <UploadCloud size={16} />

                  Add &amp; Index Document

                </>

              )}

            </button>

          </div>

        )}

      </div>


      {/* ======================================================
          Indexed Document List
      ====================================================== */}

      <div className="flex flex-col gap-3">

        <h3 className="text-sm text-slate-400 uppercase tracking-wide">

          Indexed Vector Documents ({documents.length})

        </h3>


        {documents.length === 0 ? (

          <div className="p-6 text-center bg-black/15 rounded-lg text-slate-500 text-sm">

            No documents in vector storage.

            <br />

            Upload a document to start similarity search.

          </div>

        ) : (

          <div className="flex flex-col gap-2.5 max-h-80 overflow-y-auto">

            {documents.map((doc) => (

              <div
                key={doc.doc_id}
                className="bg-white/[0.03] border border-white/10 rounded-lg px-3.5 py-3 flex items-center justify-between gap-3"
              >


                {/* Document Information */}

                <div className="flex items-center gap-2.5 overflow-hidden min-w-0">

                  <FileText
                    size={20}
                    className="text-cyan-400 shrink-0"
                  />


                  <div className="min-w-0">

                    <p className="font-semibold text-sm text-white truncate">

                      {doc.source_file}

                    </p>


                    <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-400">

                      <span className="flex items-center gap-1">

                        <Layers size={12} />

                        {doc.chunk_count} Chunks

                      </span>


                      <span>•</span>


                      <span className="font-mono">

                        ID:{' '}

                        {doc.doc_id.substring(
                          0,
                          8
                        )}

                        ...

                      </span>

                    </div>

                  </div>

                </div>


                {/* Actions */}

                <div className="flex items-center gap-1.5 shrink-0">


                  <button
                    className="inline-flex items-center gap-1 px-2 py-1.5 text-xs rounded-md bg-white/10 hover:bg-white/20 text-white transition-colors"
                    onClick={() => startUpdate(doc)}
                    title="Update Document"
                  >

                    <RefreshCw size={13} />

                    Update

                  </button>


                  <button
                    className="inline-flex items-center justify-center p-1.5 rounded-md bg-rose-500/15 hover:bg-rose-500/25 text-rose-400 transition-colors"
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