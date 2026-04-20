import { FormEvent, useRef, useState } from "react";

import { completeUpload, prepareUpload } from "@/api/documents";
import type { AuthHeaders } from "@/api/client";

type Props = {
  auth: AuthHeaders;
  onClose: () => void;
  onSuccess: () => void;
};

type Step = "form" | "uploading" | "completing" | "done" | "error";

export function UploadDocumentModal({ auth, onClose, onSuccess }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [title, setTitle] = useState("");
  const [format, setFormat] = useState("");
  const [language, setLanguage] = useState("en");
  const [step, setStep] = useState<Step>("form");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setError(null);

    try {
      setStep("uploading");
      setProgress("Preparing upload URL…");
      const prep = await prepareUpload(auth, {
        filename: file.name,
        content_type: file.type || "application/octet-stream",
        title: title || file.name,
        format: format || undefined,
        language: language || undefined,
      });

      setProgress("Uploading file…");
      const uploadRes = await fetch(prep.upload_url, {
        method: prep.method,
        headers: prep.headers,
        body: file,
      });
      if (!uploadRes.ok) throw new Error(`Upload to storage failed: ${uploadRes.status}`);

      setStep("completing");
      setProgress("Finalising…");
      await completeUpload(auth, prep.document_id);

      setStep("done");
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setStep("error");
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-md rounded-lg border border-slate-700 bg-slate-900 p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold">Upload document</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-3 rounded border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-200">
            {error}
          </div>
        )}

        {step === "done" ? (
          <div className="space-y-3 text-center">
            <p className="text-sm text-green-400">Document uploaded successfully.</p>
            <button
              type="button"
              onClick={onClose}
              className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
            >
              Close
            </button>
          </div>
        ) : step === "uploading" || step === "completing" ? (
          <div className="space-y-2 text-center py-4">
            <div className="animate-spin mx-auto h-6 w-6 rounded-full border-2 border-indigo-500 border-t-transparent" />
            <p className="text-sm text-slate-400">{progress}</p>
          </div>
        ) : (
          <form className="space-y-3" onSubmit={onSubmit}>
            <div>
              <label className="mb-1 block text-xs text-slate-400" htmlFor="doc-file">
                File <span className="text-red-400">*</span>
              </label>
              <input
                id="doc-file"
                ref={fileRef}
                type="file"
                required
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 file:mr-3 file:rounded file:border-0 file:bg-slate-800 file:px-2 file:py-1 file:text-xs file:text-slate-200"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-slate-400" htmlFor="doc-title">
                Title
              </label>
              <input
                id="doc-title"
                className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Optional display title"
              />
            </div>
            <div className="flex gap-3">
              <div className="flex-1">
                <label className="mb-1 block text-xs text-slate-400" htmlFor="doc-format">
                  Format
                </label>
                <select
                  id="doc-format"
                  className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                >
                  <option value="">Auto-detect</option>
                  <option value="pdf">PDF</option>
                  <option value="markdown">Markdown</option>
                  <option value="text">Plain text</option>
                  <option value="docx">DOCX</option>
                  <option value="html">HTML</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="mb-1 block text-xs text-slate-400" htmlFor="doc-lang">
                  Language
                </label>
                <input
                  id="doc-lang"
                  className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  placeholder="en"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded border border-slate-600 px-4 py-2 text-sm hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
              >
                Upload
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
