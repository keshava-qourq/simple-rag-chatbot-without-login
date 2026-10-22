// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { Filter, Upload } = Icons;

const PRODUCT = "Simple RAG chatbot without login";
const SCREEN = "Chat";
const MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace';

const SAMPLE_DOCS = [
  { id: "doc-001", filename: "Q3 Financial Report", file_type: "PDF", file_size_bytes: 2458624, status: "READY", chunk_count: 142, created_at: "2026-10-14", last_activity_at: "2026-10-22" },
  { id: "doc-002", filename: "Employee Handbook 2026", file_type: "DOCX", file_size_bytes: 1894400, status: "READY", chunk_count: 87, created_at: "2026-10-09", last_activity_at: "2026-10-21" },
  { id: "doc-003", filename: "Meeting Notes October", file_type: "TXT", file_size_bytes: 48200, status: "PROCESSING", chunk_count: 0, created_at: "2026-10-22", last_activity_at: "2026-10-22" },
  { id: "doc-004", filename: "Product Specs v4", file_type: "PDF", file_size_bytes: 3201400, status: "ERROR", chunk_count: 0, created_at: "2026-10-20", last_activity_at: "2026-10-20" },
  { id: "doc-005", filename: "Contract Template", file_type: "DOCX", file_size_bytes: 756800, status: "READY", chunk_count: 53, created_at: "2026-10-18", last_activity_at: "2026-10-20" },
];

const FILTERS = ["ALL", "READY", "PROCESSING", "ERROR"];

const SAMPLE_CONVERSATIONS = {
  "doc-001": [
    { question: "What was the total revenue in Q3?", answer: "Total revenue for Q3 was $4.2M, representing an 18% increase from Q2's $3.56M. The growth was primarily driven by enterprise contract renewals and the new tiered pricing model introduced in July.", timestamp: "2026-10-22 14:32" },
    { question: "How many new customers were added?", answer: "47 new customers were onboarded in Q3, compared to 31 in Q2. The acquisition cost per customer decreased from $1,240 to $980 due to improved lead qualification.", timestamp: "2026-10-22 14:35" },
  ],
  "doc-002": [
    { question: "What is the remote work policy?", answer: "Employees may work remotely up to 3 days per week with manager approval. Core hours of 10am to 3pm in the employee's time zone must be maintained for collaboration. Fully remote arrangements require a formal request and director-level approval.", timestamp: "2026-10-21 09:15" },
  ],
};

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

function generateUUID() {
  try {
    return crypto.randomUUID();
  } catch (e) {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      var v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}

export default function Screen() {
  const navigate = useNavigate();
  const [filter, setFilter] = React.useState("ALL");
  const [open, setOpen] = React.useState(null);
  const [documents, setDocuments] = React.useState(SAMPLE_DOCS);
  const [conversations, setConversations] = React.useState(SAMPLE_CONVERSATIONS);
  const [chatInput, setChatInput] = React.useState("");
  const [chatThinking, setChatThinking] = React.useState(null);
  const [uploadError, setUploadError] = React.useState(null);
  const [uuid] = React.useState(generateUUID);
  const fileInputRef = React.useRef(null);

  const thick = "3px solid " + brand.primaryColor;
  const entries = documents.filter(function (d) { return filter === "ALL" || d.status === filter; });
  var readyCount = documents.filter(function (d) { return d.status === "READY"; }).length;

  function handleFileSelect(event) {
    var file = event.target.files[0];
    if (!file) return;

    var name = file.name;
    var ext = name.split(".").pop().toLowerCase();

    if (ext !== "pdf" && ext !== "txt" && ext !== "docx") {
      setUploadError("Unsupported format: ." + ext + ". Only PDF, TXT, and DOCX files are accepted.");
      event.target.value = "";
      return;
    }

    setUploadError(null);

    var newId = "doc-" + Date.now();
    var newDoc = {
      id: newId,
      filename: name.replace(/\.[^.]+$/, ""),
      file_type: ext.toUpperCase(),
      file_size_bytes: file.size,
      status: "PROCESSING",
      chunk_count: 0,
      created_at: "2026-10-22",
      last_activity_at: "2026-10-22",
    };

    setDocuments(function (prev) { return [newDoc].concat(prev); });

    setTimeout(function () {
      setDocuments(function (prev) {
        return prev.map(function (d) {
          if (d.id === newId) {
            return Object.assign({}, d, {
              status: "READY",
              chunk_count: Math.max(1, Math.round(file.size / 2500)),
            });
          }
          return d;
        });
      });
    }, 2200);

    event.target.value = "";
  }

  function handleAskQuestion(docId) {
    if (!chatInput.trim()) return;

    var question = chatInput.trim();
    var now = new Date();
    var timestamp =
      String(now.getMonth() + 1).padStart(2, "0") + "/" +
      String(now.getDate()).padStart(2, "0") + "/" +
      now.getFullYear() + " " +
      String(now.getHours()).padStart(2, "0") + ":" +
      String(now.getMinutes()).padStart(2, "0");

    setConversations(function (prev) {
      var existing = prev[docId] || [];
      return Object.assign({}, prev, {
        [docId]: existing.concat([{ question: question, answer: null, timestamp: timestamp }]),
      });
    });
    setChatInput("");
    setChatThinking(docId);

    setTimeout(function () {
      var doc = documents.find(function (d) { return d.id === docId; });
      var answer;

      if (question.toLowerCase().indexOf("weather") !== -1 || question.toLowerCase().indexOf("recipe") !== -1) {
        answer = "No relevant information was found in your uploaded documents for this question. Try rephrasing or uploading additional documents that cover this topic.";
      } else {
        answer = "Based on " + doc.filename + ", the relevant passages indicate that this topic is addressed within the document. The system retrieved the most semantically similar chunks from the " + doc.chunk_count + " indexed segments and generated this answer using Gemini 2.5 Flash. The response is grounded in your uploaded content without citations or source references.";
      }

      setConversations(function (prev) {
        var msgs = prev[docId] || [];
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
          <p className="text-xs uppercase tracking-[0.2em]" style={{ fontFamily: MONO }}>{PRODUCT} / Documents</p>
          <p className="mt-1 text-xs" style={{ fontFamily: MONO, color: brand.neutralColor, fontVariantNumeric: "tabular-nums" }}>SESSION {uuid.slice(0, 8)} — ANONYMOUS, NO LOGIN</p>
          <h1 className="mt-2 text-7xl font-bold leading-none tracking-tight" style={{ fontFamily: brand.fontHeading }}>{SCREEN}</h1>
        </div>
        <p className="text-5xl font-bold" style={{ fontFamily: brand.fontHeading, fontVariantNumeric: "tabular-nums" }}>{String(entries.length).padStart(2, "0")}</p>
      </header>

      <nav aria-label="Filter documents" className="flex gap-6 py-4 items-center" style={{ borderBottom: thick, fontFamily: MONO }}>
        {FILTERS.map(function (f) {
          return (
            <button
              key={f}
              type="button"
              aria-pressed={filter === f}
              onClick={function () { setFilter(f); }}
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
            }}
          >
            <Upload size={14} aria-hidden="true" />
            UPLOAD
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.docx"
              className="hidden"
              onChange={handleFileSelect}
              aria-label="Upload document (PDF, TXT, or DOCX)"
            />
          </label>
        </div>
      </nav>

      {entries.length === 0 ? (
        <div className="mt-8 p-12 text-center" style={{ border: thick, boxShadow: "6px 6px 0 " + brand.primaryColor, backgroundColor: brand.backgroundColor }}>
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
            return (
              <li key={doc.id}>
                <button
                  type="button"
                  onClick={function () { toggleOpen(doc.id); }}
                  aria-expanded={open === doc.id}
                  className="grid w-full grid-cols-[96px_minmax(0,1fr)_auto] items-center gap-6 p-5 text-left transition-transform hover:-translate-x-1 hover:-translate-y-1"
                  style={{
                    border: thick,
                    borderRadius: brand.radius,
                    boxShadow: "6px 6px 0 " + (doc.status === "ERROR" ? brand.accentColor : brand.primaryColor),
                    backgroundColor: brand.backgroundColor,
                  }}
                >
                  <span className="text-5xl font-bold" style={{ fontFamily: brand.fontHeading, fontVariantNumeric: "tabular-nums" }}>
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span>
                    <span className="block text-3xl font-bold leading-tight" style={{ fontFamily: brand.fontHeading }}>
                      {doc.filename}
                    </span>
                    <span className="mt-1 block text-xs" style={{ fontFamily: MONO }}>
                      {doc.file_type} · {doc.created_at} · {doc.status}
                    </span>
                  </span>
                  <span className="text-lg font-bold" style={{ fontFamily: MONO, fontVariantNumeric: "tabular-nums" }}>
                    {doc.chunk_count > 0 ? doc.chunk_count + " CHUNKS" : formatBytes(doc.file_size_bytes)}
                  </span>
                </button>
                {open === doc.id ? (
                  <div style={{ borderLeft: thick, borderRight: thick, borderBottom: thick, fontFamily: MONO }}>
                    <div
                      className="p-5 grid grid-cols-2 gap-x-8 gap-y-2 text-sm"
                      style={{ borderBottom: doc.status === "READY" ? "1px dashed " + brand.neutralColor : "none" }}
                    >
                      <div><span style={{ color: brand.neutralColor }}>FILE TYPE</span> {doc.file_type}</div>
                      <div><span style={{ color: brand.neutralColor }}>SIZE</span> {formatBytes(doc.file_size_bytes)}</div>
                      <div><span style={{ color: brand.neutralColor }}>CHUNKS</span> {doc.chunk_count}</div>
                      <div><span style={{ color: brand.neutralColor }}>STATUS</span> {doc.status}</div>
                      <div><span style={{ color: brand.neutralColor }}>UPLOADED</span> {doc.created_at}</div>
                      <div><span style={{ color: brand.neutralColor }}>LAST ACTIVITY</span> {doc.last_activity_at}</div>
                      <div className="col-span-2"><span style={{ color: brand.neutralColor }}>DOC ID</span> {doc.id}</div>
                    </div>

                    {doc.status === "PROCESSING" ? (
                      <div className="p-5 text-sm">
                        <p className="font-bold">Parsing and embedding in progress…</p>
                        <p className="mt-2" style={{ color: brand.neutralColor }}>
                          Extracting text, chunking with overlap, and generating embeddings via gemini-embedding-001. This document will be ready to chat against shortly.
                        </p>
                      </div>
                    ) : null}

                    {doc.status === "ERROR" ? (
                      <div className="p-5 text-sm">
                        <p className="font-bold" style={{ color: brand.accentColor }}>PROCESSING FAILED</p>
                        <p className="mt-2" style={{ color: brand.neutralColor }}>
                          An error occurred while parsing or embedding this document. The file may be corrupted or password-protected. Please re-upload a valid {doc.file_type} file.
                        </p>
                      </div>
                    ) : null}

                    {doc.status === "READY" ? (
                      <div className="p-5">
                        <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: brand.neutralColor }}>Conversation History</p>
                        {(conversations[doc.id] || []).length === 0 && chatThinking !== doc.id ? (
                          <p className="text-sm" style={{ color: brand.neutralColor }}>
                            No questions asked yet. Type a question below to chat with this document.
                          </p>
                        ) : (
                          <div className="space-y-4 mb-4">
                            {(conversations[doc.id] || []).map(function (msg, i) {
                              return (
                                <div key={i}>
                                  <div className="text-sm">
                                    <span className="font-bold" style={{ color: brand.accentColor }}>Q </span>
                                    <span>{msg.question}</span>
                                  </div>
                                  <div className="mt-1 text-sm">
                                    <span className="font-bold">A </span>
                                    {msg.answer === null ? (
                                      <span style={{ color: brand.neutralColor }}>Generating answer with Gemini 2.5 Flash…</span>
                                    ) : (
                                      <span>{msg.answer}</span>
                                    )}
                                  </div>
                                  <div className="mt-1 text-xs" style={{ color: brand.neutralColor, fontVariantNumeric: "tabular-nums" }}>
                                    {msg.timestamp}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        <div className="flex gap-3 mt-4" style={{ borderTop: "1px dashed " + brand.neutralColor, paddingTop: "1rem" }}>
                          <input
                            type="text"
                            value={chatInput}
                            onChange={function (e) { setChatInput(e.target.value); }}
                            onKeyDown={function (e) { if (e.key === "Enter") handleAskQuestion(doc.id); }}
                            placeholder="Ask a question about this document…"
                            className="flex-1 px-3 py-2 text-sm"
                            style={{ border: thick, fontFamily: MONO, backgroundColor: brand.backgroundColor, color: brand.primaryColor }}
                            aria-label={"Ask a question about " + doc.filename}
                          />
                          <button
                            type="button"
                            onClick={function () { handleAskQuestion(doc.id); }}
                            disabled={chatThinking === doc.id || !chatInput.trim()}
                            className="px-4 py-2 text-sm font-bold"
                            style={{
                              border: thick,
                              fontFamily: MONO,
                              backgroundColor: brand.primaryColor,
                              color: brand.backgroundColor,
                              cursor: chatThinking === doc.id || !chatInput.trim() ? "not-allowed" : "pointer",
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
          onClick={function () { navigate("docs"); }}
          className="font-bold underline"
          style={{ color: brand.primaryColor, textDecorationThickness: 2, textUnderlineOffset: 3 }}
        >
          Read the documentation →
        </button>
      </p>
    </div>
  );
}
