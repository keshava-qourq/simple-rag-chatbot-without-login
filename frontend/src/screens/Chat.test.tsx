import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Screen from "./Chat";
import { UploadError } from "@/lib/documents";

const { fetchDocuments, fetchDocumentStatus, uploadDocument } = vi.hoisted(() => ({
  fetchDocuments: vi.fn(),
  fetchDocumentStatus: vi.fn(),
  uploadDocument: vi.fn(),
}));

vi.mock("@/lib/documents", async () => {
  const actual = await vi.importActual<typeof import("@/lib/documents")>("@/lib/documents");
  return {
    ...actual,
    fetchDocuments,
    fetchDocumentStatus,
    uploadDocument,
  };
});

function renderScreen() {
  return render(
    <MemoryRouter>
      <Screen />
    </MemoryRouter>,
  );
}

function makeFile(name: string, type = "text/plain") {
  return new File(["hello world"], name, { type });
}

beforeEach(() => {
  window.localStorage.clear();
  fetchDocuments.mockReset();
  fetchDocumentStatus.mockReset();
  uploadDocument.mockReset();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("Chat screen document list", () => {
  it("shows a loading state before the document list resolves", async () => {
    let resolve: (value: unknown) => void;
    fetchDocuments.mockReturnValue(
      new Promise((r) => {
        resolve = r;
      }),
    );
    renderScreen();
    expect(screen.getByText("Loading documents…")).toBeInTheDocument();
    resolve!([]);
    await waitFor(() => expect(screen.queryByText("Loading documents…")).not.toBeInTheDocument());
  });

  it("shows an empty state with no seeded data when the API returns no documents", async () => {
    fetchDocuments.mockResolvedValue([]);
    renderScreen();
    await waitFor(() => expect(screen.getByText("No documents uploaded yet")).toBeInTheDocument());
    expect(screen.queryByText("Q3 Financial Report")).not.toBeInTheDocument();
  });

  it("shows an error state when the document list fails to load", async () => {
    fetchDocuments.mockRejectedValue(new Error("network down"));
    renderScreen();
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("network down"));
  });

  it("renders documents from the API response", async () => {
    fetchDocuments.mockResolvedValue([
      { id: "doc-1", filename: "report.pdf", status: "PROCESSED" },
    ]);
    renderScreen();
    await waitFor(() => expect(screen.getByText("report.pdf")).toBeInTheDocument());
  });
});

describe("Chat screen upload", () => {
  it("has an accessible label on the upload control", async () => {
    fetchDocuments.mockResolvedValue([]);
    renderScreen();
    await waitFor(() => expect(fetchDocuments).toHaveBeenCalled());
    expect(screen.getByLabelText("Upload document (PDF, TXT, or DOCX)")).toBeInTheDocument();
  });

  it("blocks unsupported file types and shows an alert", async () => {
    fetchDocuments.mockResolvedValue([]);
    renderScreen();
    await waitFor(() => expect(fetchDocuments).toHaveBeenCalled());

    const input = screen.getByLabelText("Upload document (PDF, TXT, or DOCX)");
    fireEvent.change(input, { target: { files: [makeFile("image.png", "image/png")] } });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Only PDF, TXT, and DOCX files are supported.");
    expect(uploadDocument).not.toHaveBeenCalled();
  });

  it("uploads a valid file with the browser UUID and adds it to the list", async () => {
    fetchDocuments.mockResolvedValue([]);
    uploadDocument.mockResolvedValue({ id: "doc-99", filename: "notes.txt", status: "PROCESSED" });
    renderScreen();
    await waitFor(() => expect(fetchDocuments).toHaveBeenCalled());

    const input = screen.getByLabelText("Upload document (PDF, TXT, or DOCX)");
    fireEvent.change(input, { target: { files: [makeFile("notes.txt")] } });

    await waitFor(() => expect(screen.getByText("notes.txt")).toBeInTheDocument());
    expect(uploadDocument).toHaveBeenCalledTimes(1);
    const [, uuidArg] = uploadDocument.mock.calls[0];
    expect(typeof uuidArg).toBe("string");
    expect(uuidArg.length).toBeGreaterThan(0);
  });

  it("renders the server's error message on a rejected upload", async () => {
    fetchDocuments.mockResolvedValue([]);
    uploadDocument.mockRejectedValue(
      new UploadError("Only PDF, TXT, and DOCX files are accepted."),
    );
    renderScreen();
    await waitFor(() => expect(fetchDocuments).toHaveBeenCalled());

    const input = screen.getByLabelText("Upload document (PDF, TXT, or DOCX)");
    fireEvent.change(input, { target: { files: [makeFile("notes.pdf", "application/pdf")] } });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Only PDF, TXT, and DOCX files are accepted.");
  });
});

describe("Chat screen status polling", () => {
  it("polls a pending document's status until it reaches a terminal state", async () => {
    fetchDocuments.mockResolvedValue([{ id: "doc-5", filename: "big.pdf", status: "PENDING" }]);
    fetchDocumentStatus.mockResolvedValue({ id: "doc-5", status: "PROCESSED" });

    renderScreen();

    await waitFor(() => expect(screen.getByText("big.pdf")).toBeInTheDocument());

    await waitFor(
      () => expect(fetchDocumentStatus).toHaveBeenCalledWith("doc-5", expect.any(String)),
      { timeout: 3000 },
    );
  });
});
