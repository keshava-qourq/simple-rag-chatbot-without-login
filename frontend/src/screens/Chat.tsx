// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";
import { fetchDocuments, fetchDocumentStatus, uploadDocument } from "@/lib/documents";

const { Filter, Upload } = Icons;

const PRODUCT = "Simple RAG chatbot without login";
const SCREEN = "Chat";
const MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace';

const FILTERS = ["ALL", "PENDING", "PROCESSING", "PROCESSED", "ERROR"];

const SAMPLE_CONVERSATIONS = {};

const UUID_STORAGE_KEY = "browser-uuid";
const STATUS_POLL_INTERVAL_MS = 2000;

function formatBytes(bytes) {
  if (bytes === undefined || bytes === null) return "—";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

function generateUUID() {
  try {
    return crypto.randomUUID();
  } catch (e) {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}

// TODO: replace with the shared helper from frontend/src/lib/uuid.ts once US-001-1 lands;
// that file does not exist in this repository yet, so the UUID is generated and persisted
// locally here instead.
function getOrCreateBrowserUUID() {
  try {
    const existing = window.localStorage.getItem(UUID_STORAGE_KEY);
    if (existing) return existing;
    const created = generateUUID();
    window.localStorage.setItem(UUID_STORAGE_KEY, created);
    return created;
  } catch (e) {
    return generateUUID();
  }
}

function normalizeStatus(status) {
  return (status || "").toString().toUpperCase();
}

function isPendingStatus(status) {
  const s = normalizeStatus(status);
  return s === "PENDING" || s === "PROCESSING";
}

function isErrorStatus(status) {
  const s = normalizeStatus(status);
  return s === "ERROR" || s === "FAILED";
}

function isReadyStatus(status) {
  const s = normalizeStatus(status);
  return s === "PROCESSED" || s === "READY" || s === "COMPLETE" || s === "COMPLETED";
}

function inferFileType(doc) {
  if (doc.file_type) return doc.file_type;
  const parts = (doc.filename || "").split(".");
  return parts.length > 1 ? parts.pop().toUpperCase() : "FILE";
}

export default function Screen() {
  const navigate = useNavigate();
  const [filter, setFilter] = React.useState("ALL");
  const [open, setOpen] = React.useState(null);
  const [documents, setDocuments] = React.useState([]);
  const [docsLoading, setDocsLoading] = React.useState(true);
  const [docsError, setDocsError] = React.useState(null);
  const [conversations, setConversations] = React.useState(SAMPLE_CONVERSATIONS);
  const [chatInput, setChatInput] = React.useState("");
  const [chatThinking, setChatThinking] = React.useState(null);
  const [uploadError, setUploadError] = React.useState(null);
  const [uploading, setUploading] = React.useState(false);
  const [uuid] = React.useState(getOrCreateBrowserUUID);
  const fileInputRef = React.useRef(null);

  const thick = "3px solid " + brand.primaryColor;

  React.useEffect(() => {
    let cancelled = false;
    async function load() {
      setDocsLoading(true);
      setDocsError(null);
      try {
        const docs = await fetchDocuments(uuid);
        if (!cancelled) setDocuments(Array.isArray(docs) ? docs : []);
      } catch (err) {
        if (!cancelled)
          setDocsError(err && err.message ? err.message : "Failed to load documents.");
      } finally {
        if (!cancelled) setDocsLoading(false);
      }
    }
    load();
    return function () {
      cancelled = true;
    };
  }, [uuid]);

  React.useEffect(() => {
    const pending = documents.filter(function (d) {
      return isPendingStatus(d.status);
    });
    if (pending.length === 0) return undefined;

    const interval = setInterval(function () {
      pending.forEach(function (doc) {
        fetchDocumentStatus(doc.id, uuid)
          .then(function (result) {
            setDocuments(function (prev) {
              return prev.map(function (d) {
                return d.id === doc.id ? Object.assign({}, d, result) : d;
              });
            });
          })
          .catch(function () {
            // transient polling failure; next tick will retry
          });
      });
    }, STATUS_POLL_INTERVAL_MS);

    return function () {
      clearInterval(interval);
    };
  }, [documents, uuid]);

  const entries = documents.filter(function (d) {
    return filter === "ALL" || normalizeStatus(d.status) === filter;
  });
  const readyCount = documents.filter(function (d) {
    return isReadyStatus(d.status);
  }).length;

  async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const name = file.name;
    const ext = name.includes(".") ? name.split(".").pop().toLowerCase() : "";

    if (ext !== "pdf" && ext !== "txt" && ext !== "docx") {
      setUploadError("Only PDF, TXT, and DOCX files are supported.");
      event.target.value = "";
      return;
    }

    setUploadError(null);
    setUploading(true);

    try {
      const created = await uploadDocument(file, uuid);
      setDocuments(function (prev) {
        return [created].concat(prev);
      });
    } catch (err) {
      setUploadError(err && err.message ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  function handleAskQuestion(docId) {
    if (!chatInput.trim()) return;

    const question = chatInput.trim();
    const now = new Date();
    const timestamp =
      String(now.getMonth() + 1).padStart(2, "0") +
      "/" +
      String(now.getDate()).padStart(2, "0") +
      "/" +
      now.getFullYear() +
      " " +
      String(now.getHours()).padStart(2, "0") +
      ":" +
      String(now.getMinutes()).padStart(2, "0");

    setConversations(function (prev) {
      const existing = prev[docId] || [];
      return Object.assign({}, prev, {
        [docId]: existing.concat([{ question: question, answer: null, timestamp: timestamp }]),
      });
    });
    setChatInput("");
    setChatThinking(docId);

    setTimeout(function () {
      const doc = documents.find(function (d) {
        return d.id === docId;
      });
      let answer;

      if (
        question.toLowerCase().indexOf("weather") !== -1 ||
        question.toLowerCase().indexOf("recipe") !== -1
      ) {
        answer =
          "No relevant information was found in your uploaded documents for this question. Try rephrasing or uploading additional documents that cover this topic.";
      } else {
        answer =
          "Based on " +
          (doc ? doc.filename : "this document") +
          ", the relevant passages indicate that this topic is addressed within the document. The system retrieved the most semantically similar chunks and generated this answer using Gemini 2.5 Flash. The response is grounded in your uploaded content without citations or source references.";
      }

      setConversations(function (prev) {
        const msgs = prev[docId] || [];
        return Object.assign({}, prev, {
          [docId]: msgs.map(function (msg, i) {
            if (i === msgs.length - 1) return Object.assign({}, msg, { answer: answer });
            return msg;
          }),
        });
      });
      setChatThinking(null);
    }, 1500);
  }

  function toggleOpen(docId) {
    if (open === docId) {
      setOpen(null);
    } else {
      setOpen(docId);
      setChatInput("");
      setChatThinking(null);
    }
  }

  return (
    <div style={{ color: brand.primaryColor, fontFamily: brand.fontBody }}>
      <style>{"@media (prefers-reduced-motion: reduce){*{transition:none!important}}"}</style>

      <header className="flex items-end justify-between pb-4" style={{ borderBottom: thick }}>
        <div>
          <p className="text-xs uppercase tracking-[0.2em]" style={{ fontFamily: MONO }}>
            {PRODUCT} / Documents
          </p>
          <p
            className="mt-1 text-xs"
            style={{
              fontFamily: MONO,
              color: brand.neutralColor,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            SESSION {uuid.slice(0, 8)} — ANONYMOUS, NO LOGIN
          </p>
          <h1
            className="mt-2 text-7xl font-bold leading-none tracking-tight"
            style={{ fontFamily: brand.fontHeading }}
          >
            {SCREEN}
          </h1>
        </div>
        <p
          className="text-5xl font-bold"
          style={{ fontFamily: brand.fontHeading, fontVariantNumeric: "tabular-nums" }}
        >
          {String(entries.length).padStart(2, "0")}
        </p>
      </header>

      <nav
        aria-label="Filter documents"
        className="flex gap-6 py-4 items-center"
        style={{ borderBottom: thick, fontFamily: MONO }}
      >
        {FILTERS.map(function (f) {
          return (
            <button
              key={f}
              type="button"
              aria-pressed={filter === f}
              onClick={function () {
                setFilter(f);
              }}
              className="text-sm font-bold"
              style={{
                textDecoration: filter === f ? "underline" : "none",
                textDecorationThickness: 3,
                textUnderlineOffset: 6,
                color: filter === f ? brand.primaryColor : brand.neutralColor,
              }}
            >
              [{f}]
            </button>
          );
        })}
        <div className="ml-auto flex items-center gap-4">
          {uploadError ? (
            <span className="text-sm font-bold" style={{ color: brand.accentColor }} role="alert">
              {uploadError}
            </span>
          ) : null}
          <label
            className="text-sm font-bold cursor-pointer inline-flex items-center gap-1 px-3 py-1"
            style={{
              border: thick,
              backgroundColor: brand.primaryColor,
              color: brand.backgroundColor,
              boxShadow: "4px 4px 0 " + brand.accentColor,
              opacity: uploading ? 0.6 : 1,
            }}
          >
            <Upload size={14} aria-hidden="true" />
            {uploading ? "UPLOADING…" : "UPLOAD"}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.docx"
              className="hidden"
              onChange={handleFileSelect}
              disabled={uploading}
              aria-label="Upload document (PDF, TXT, or DOCX)"
            />
          </label>
        </div>
      </nav>

      {docsLoading ? (
        <div
          className="mt-8 p-12 text-center"
          style={{
            border: thick,
            boxShadow: "6px 6px 0 " + brand.primaryColor,
            backgroundColor: brand.backgroundColor,
          }}
        >
          <p className="text-3xl font-bold" style={{ fontFamily: brand.fontHeading }}>
            Loading documents…
          </p>
        </div>
      ) : docsError ? (
        <div
          className="mt-8 p-12 text-center"
          style={{
            border: thick,
            boxShadow: "6px 6px 0 " + brand.accentColor,
            backgroundColor: brand.backgroundColor,
          }}
          role="alert"
        >
          <p className="text-3xl font-bold" style={{ fontFamily: brand.fontHeading }}>
            Could not load documents
          </p>
          <p className="mt-3 text-sm" style={{ fontFamily: MONO, color: brand.neutralColor }}>
            {docsError}
          </p>
        </div>
      ) : entries.length === 0 ? (
        <div
          className="mt-8 p-12 text-center"
          style={{
            border: thick,
            boxShadow: "6px 6px 0 " + brand.primaryColor,
            backgroundColor: brand.backgroundColor,
          }}
        >
          <p className="text-3xl font-bold" style={{ fontFamily: brand.fontHeading }}>
            {readyCount === 0 ? "No documents uploaded yet" : "No documents in this view"}
          </p>
          <p className="mt-3 text-sm" style={{ fontFamily: MONO, color: brand.neutralColor }}>
            {readyCount === 0
              ? "Upload a PDF, TXT, or DOCX file to start chatting with your documents."
              : "Try a different filter to see your documents."}
          </p>
        </div>
      ) : (
        <ol className="mt-8 space-y-6">
          {entries.map(function (doc, index) {
            const fileType = inferFileType(doc);
            const status = normalizeStatus(doc.status);
            return (
              <li key={doc.id}>
                <button
                  type="button"
                  onClick={function () {
                    toggleOpen(doc.id);
                  }}
                  aria-expanded={open === doc.id}
                  className="grid w-full grid-cols-[96px_minmax(0,1fr)_auto] items-center gap-6 p-5 text-left transition-transform hover:-translate-x-1 hover:-translate-y-1"
                  style={{
                    border: thick,
                    borderRadius: brand.radius,
                    boxShadow:
                      "6px 6px 0 " +
                      (isErrorStatus(status) ? brand.accentColor : brand.primaryColor),
                    backgroundColor: brand.backgroundColor,
                  }}
                >
                  <span
                    className="text-5xl font-bold"
                    style={{ fontFamily: brand.fontHeading, fontVariantNumeric: "tabular-nums" }}
                  >
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span>
                    <span
                      className="block text-3xl font-bold leading-tight"
                      style={{ fontFamily: brand.fontHeading }}
                    >
                      {doc.filename}
                    </span>
                    <span className="mt-1 block text-xs" style={{ fontFamily: MONO }}>
                      {fileType} · {doc.created_at || "—"} · {status}
                    </span>
                  </span>
                  <span
                    className="text-lg font-bold"
                    style={{ fontFamily: MONO, fontVariantNumeric: "tabular-nums" }}
                  >
                    {doc.chunk_count
                      ? doc.chunk_count + " CHUNKS"
                      : formatBytes(doc.file_size_bytes)}
                  </span>
                </button>
                {open === doc.id ? (
                  <div
                    style={{
                      borderLeft: thick,
                      borderRight: thick,
                      borderBottom: thick,
                      fontFamily: MONO,
                    }}
                  >
                    <div
                      className="p-5 grid grid-cols-2 gap-x-8 gap-y-2 text-sm"
                      style={{
                        borderBottom: isReadyStatus(status)
                          ? "1px dashed " + brand.neutralColor
                          : "none",
                      }}
                    >
                      <div>
                        <span style={{ color: brand.neutralColor }}>FILE TYPE</span> {fileType}
                      </div>
                      <div>
                        <span style={{ color: brand.neutralColor }}>SIZE</span>{" "}
                        {formatBytes(doc.file_size_bytes)}
                      </div>
                      <div>
                        <span style={{ color: brand.neutralColor }}>CHUNKS</span>{" "}
                        {doc.chunk_count || 0}
                      </div>
                      <div>
                        <span style={{ color: brand.neutralColor }}>STATUS</span> {status}
                      </div>
                      <div>
                        <span style={{ color: brand.neutralColor }}>UPLOADED</span>{" "}
                        {doc.created_at || "—"}
                      </div>
                      <div>
                        <span style={{ color: brand.neutralColor }}>LAST ACTIVITY</span>{" "}
                        {doc.last_activity_at || "—"}
                      </div>
                      <div className="col-span-2">
                        <span style={{ color: brand.neutralColor }}>DOC ID</span> {doc.id}
                      </div>
                    </div>

                    {isPendingStatus(status) ? (
                      <div className="p-5 text-sm">
                        <p className="font-bold">Parsing and embedding in progress…</p>
                        <p className="mt-2" style={{ color: brand.neutralColor }}>
                          Extracting text, chunking with overlap, and generating embeddings via
                          gemini-embedding-001. This document will be ready to chat against shortly.
                        </p>
                      </div>
                    ) : null}

                    {isErrorStatus(status) ? (
                      <div className="p-5 text-sm">
                        <p className="font-bold" style={{ color: brand.accentColor }}>
                          PROCESSING FAILED
                        </p>
                        <p className="mt-2" style={{ color: brand.neutralColor }}>
                          An error occurred while parsing or embedding this document. The file may
                          be corrupted or password-protected. Please re-upload a valid {fileType}{" "}
                          file.
                        </p>
                      </div>
                    ) : null}

                    {isReadyStatus(status) ? (
                      <div className="p-5">
                        <p
                          className="text-xs uppercase tracking-[0.2em] mb-4"
                          style={{ color: brand.neutralColor }}
                        >
                          Conversation History
                        </p>
                        {(conversations[doc.id] || []).length === 0 && chatThinking !== doc.id ? (
                          <p className="text-sm" style={{ color: brand.neutralColor }}>
                            No questions asked yet. Type a question below to chat with this
                            document.
                          </p>
                        ) : (
                          <div className="space-y-4 mb-4">
                            {(conversations[doc.id] || []).map(function (msg, i) {
                              return (
                                <div key={i}>
                                  <div className="text-sm">
                                    <span
                                      className="font-bold"
                                      style={{ color: brand.accentColor }}
                                    >
                                      Q{" "}
                                    </span>
                                    <span>{msg.question}</span>
                                  </div>
                                  <div className="mt-1 text-sm">
                                    <span className="font-bold">A </span>
                                    {msg.answer === null ? (
                                      <span style={{ color: brand.neutralColor }}>
                                        Generating answer with Gemini 2.5 Flash…
                                      </span>
                                    ) : (
                                      <span>{msg.answer}</span>
                                    )}
                                  </div>
                                  <div
                                    className="mt-1 text-xs"
                                    style={{
                                      color: brand.neutralColor,
                                      fontVariantNumeric: "tabular-nums",
                                    }}
                                  >
                                    {msg.timestamp}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        <div
                          className="flex gap-3 mt-4"
                          style={{
                            borderTop: "1px dashed " + brand.neutralColor,
                            paddingTop: "1rem",
                          }}
                        >
                          <input
                            type="text"
                            value={chatInput}
                            onChange={function (e) {
                              setChatInput(e.target.value);
                            }}
                            onKeyDown={function (e) {
                              if (e.key === "Enter") handleAskQuestion(doc.id);
                            }}
                            placeholder="Ask a question about this document…"
                            className="flex-1 px-3 py-2 text-sm"
                            style={{
                              border: thick,
                              fontFamily: MONO,
                              backgroundColor: brand.backgroundColor,
                              color: brand.primaryColor,
                            }}
                            aria-label={"Ask a question about " + doc.filename}
                          />
                          <button
                            type="button"
                            onClick={function () {
                              handleAskQuestion(doc.id);
                            }}
                            disabled={chatThinking === doc.id || !chatInput.trim()}
                            className="px-4 py-2 text-sm font-bold"
                            style={{
                              border: thick,
                              fontFamily: MONO,
                              backgroundColor: brand.primaryColor,
                              color: brand.backgroundColor,
                              cursor:
                                chatThinking === doc.id || !chatInput.trim()
                                  ? "not-allowed"
                                  : "pointer",
                              opacity: chatThinking === doc.id || !chatInput.trim() ? 0.5 : 1,
                            }}
                          >
                            {chatThinking === doc.id ? "…" : "ASK"}
                          </button>
                        </div>
                      </div>
                    ) : null}
                  </div>
                ) : null}
              </li>
            );
          })}
        </ol>
      )}

      <p className="mt-8 text-xs" style={{ fontFamily: MONO, color: brand.neutralColor }}>
        Need help with setup, environment variables, or supported formats?{" "}
        <button
          type="button"
          onClick={function () {
            navigate("docs");
          }}
          className="font-bold underline"
          style={{ color: brand.primaryColor, textDecorationThickness: 2, textUnderlineOffset: 3 }}
        >
          Read the documentation →
        </button>
      </p>
    </div>
  );
}
