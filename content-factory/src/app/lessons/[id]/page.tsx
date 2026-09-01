"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  api,
  Lesson,
  Unit,
  Course,
  CurriculumSource,
  ExtractionResponse,
} from "@/lib/api";

const ACCEPTED_EXTENSIONS = ".pptx,.pdf,.docx,.xlsx";

export default function LessonDetailPage() {
  const params = useParams();
  const lessonId = params.id as string;

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [unit, setUnit] = useState<Unit | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [curriculum, setCurriculum] = useState<CurriculumSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Extraction state
  const [extractingId, setExtractingId] = useState<string | null>(null);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [extractionSuccess, setExtractionSuccess] = useState<string | null>(null);
  const [viewingExtraction, setViewingExtraction] = useState<ExtractionResponse | null>(null);
  const [viewingExtractionLoading, setViewingExtractionLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const l = await api.getLesson(lessonId);
      setLesson(l);

      // Fetch parent unit and course
      const u = await api.getUnit(l.unit_id);
      setUnit(u);
      if (u) {
        const c = await api.getCourse(u.course_id);
        setCourse(c);
      }

      const sources = await api.listCurriculum(lessonId);
      setCurriculum(sources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load lesson");
    } finally {
      setLoading(false);
    }
  }, [lessonId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const refreshCurriculum = useCallback(async () => {
    try {
      const sources = await api.listCurriculum(lessonId);
      setCurriculum(sources);
    } catch {
      // ignore
    }
  }, [lessonId]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadError(null);
    setSuccessMessage(null);

    try {
      const record = await api.uploadCurriculum(lessonId, selectedFile);
      setSuccessMessage(`"${record.original_filename}" uploaded successfully.`);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      setTimeout(() => setSuccessMessage(null), 5000);
      await refreshCurriculum();
    } catch (err) {
      setUploadError(
        err instanceof Error ? err.message : "Failed to upload file",
      );
    } finally {
      setUploading(false);
    }
  };

  const handleExtract = async (sourceId: string) => {
    setExtractingId(sourceId);
    setExtractionError(null);
    setExtractionSuccess(null);

    try {
      const result = await api.extractCurriculum(sourceId);
      setExtractionSuccess(
        `Extraction complete: ${result.extracted_data?.metadata?.slide_count ?? 0} slides extracted.`,
      );
      setTimeout(() => setExtractionSuccess(null), 5000);
      await refreshCurriculum();
      // Auto-show the extraction
      setViewingExtraction(result);
    } catch (err) {
      setExtractionError(
        err instanceof Error ? err.message : "Extraction failed",
      );
    } finally {
      setExtractingId(null);
    }
  };

  const handleViewExtraction = async (sourceId: string) => {
    setViewingExtractionLoading(true);
    setExtractionError(null);

    try {
      const result = await api.getExtraction(sourceId);
      setViewingExtraction(result);
    } catch (err) {
      setExtractionError(
        err instanceof Error ? err.message : "Failed to load extraction",
      );
    } finally {
      setViewingExtractionLoading(false);
    }
  };

  if (loading) {
    return <div className="text-gray-500">Loading lesson...</div>;
  }

  if (error && !lesson) {
    return (
      <div className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div>
      {/* Breadcrumb */}
      <nav className="mb-4 text-sm text-gray-500">
        {course && (
          <>
            <Link href="/courses" className="hover:text-indigo-600">
              Courses
            </Link>
            <span className="mx-2">/</span>
            <Link
              href={`/courses/${course.id}`}
              className="hover:text-indigo-600"
            >
              {course.name}
            </Link>
            <span className="mx-2">/</span>
          </>
        )}
        {unit && (
          <>
            <span className="text-gray-700">Unit {unit.number}: {unit.title}</span>
            <span className="mx-2">/</span>
          </>
        )}
        <span className="text-gray-700">
          Lesson {lesson?.number}: {lesson?.title}
        </span>
      </nav>

      {/* Lesson info */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          Lesson {lesson?.number}: {lesson?.title}
        </h1>
        <div className="mt-2 flex items-center gap-4 text-sm">
          {course && (
            <span className="text-gray-600">
              Course: <span className="font-medium text-gray-900">{course.name}</span>
            </span>
          )}
          {unit && (
            <span className="text-gray-600">
              Unit: <span className="font-medium text-gray-900">{unit.number} — {unit.title}</span>
            </span>
          )}
          <span className="text-gray-600">
            Status:{" "}
            <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
              {lesson?.status}
            </span>
          </span>
        </div>
      </div>

      {successMessage && (
        <div className="mb-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
          {successMessage}
        </div>
      )}

      {extractionSuccess && (
        <div className="mb-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
          {extractionSuccess}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Curriculum Sources section */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Curriculum Sources</h2>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          Upload Curriculum
        </button>
      </div>

      {/* Upload form (hidden file input + submit button) */}
      <form onSubmit={handleUpload} className="mb-6">
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          onChange={handleFileSelect}
          className="hidden"
        />
        {selectedFile && (
          <div className="mb-3 flex items-center gap-3 rounded-md border border-gray-200 bg-white px-4 py-3 shadow-sm">
            <span className="text-sm text-gray-700">
              Selected: <span className="font-medium">{selectedFile.name}</span>
            </span>
            <span className="text-xs text-gray-400">
              ({(selectedFile.size / 1024).toFixed(1)} KB)
            </span>
            <button
              type="submit"
              disabled={uploading}
              className="ml-auto rounded-md bg-green-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50"
            >
              {uploading ? "Uploading..." : "Confirm Upload"}
            </button>
            <button
              type="button"
              onClick={() => {
                setSelectedFile(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = "";
                }
              }}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        )}
        {uploading && (
          <div className="mb-3 text-sm text-gray-500">Uploading file...</div>
        )}
        {uploadError && (
          <div className="mb-3 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
            {uploadError}
          </div>
        )}
      </form>

      {/* Curriculum list */}
      {curriculum.length === 0 && !uploading && (
        <p className="text-gray-500">
          No curriculum files uploaded yet.
        </p>
      )}

      {curriculum.length > 0 && (
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-gray-200 text-left text-sm text-gray-500">
              <th className="py-3 pr-4 font-medium">Filename</th>
              <th className="py-3 pr-4 font-medium">Type</th>
              <th className="py-3 pr-4 font-medium">Uploaded</th>
              <th className="py-3 pr-4 font-medium">Status</th>
              <th className="py-3 pr-4 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {curriculum.map((src) => (
              <tr key={src.id} className="border-b border-gray-100 text-sm">
                <td className="py-3 pr-4 font-medium text-gray-900">
                  {src.original_filename}
                </td>
                <td className="py-3 pr-4 text-gray-600 uppercase">
                  {src.file_type || "—"}
                </td>
                <td className="py-3 pr-4 text-gray-500">
                  {new Date(src.uploaded_at).toLocaleString()}
                </td>
                <td className="py-3 pr-4">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      src.processing_status === "completed"
                        ? "bg-green-100 text-green-800"
                        : src.processing_status === "failed"
                          ? "bg-red-100 text-red-800"
                          : src.processing_status === "processing"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {src.processing_status}
                  </span>
                </td>
                <td className="py-3 pr-4">
                  <div className="flex items-center gap-2">
                    {src.file_type === "pptx" && (
                      <button
                        onClick={() => handleExtract(src.id)}
                        disabled={extractingId === src.id}
                        className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                      >
                        {extractingId === src.id ? "Extracting..." : "Extract"}
                      </button>
                    )}
                    {src.processing_status === "completed" && (
                      <button
                        onClick={() => handleViewExtraction(src.id)}
                        disabled={viewingExtractionLoading}
                        className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                      >
                        {viewingExtractionLoading ? "Loading..." : "View Extraction"}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Extraction error */}
      {extractionError && (
        <div className="mt-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
          {extractionError}
        </div>
      )}

      {/* Extraction viewer panel */}
      {viewingExtraction && viewingExtraction.extracted_data && (
        <div className="mt-6 rounded-md border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Extracted Content — {viewingExtraction.original_filename}
            </h3>
            <button
              onClick={() => setViewingExtraction(null)}
              className="rounded-md border border-gray-300 px-3 py-1 text-xs text-gray-600 hover:bg-gray-50"
            >
              Close
            </button>
          </div>

          {/* Metadata */}
          <div className="mb-4 flex items-center gap-4 text-sm text-gray-500">
            <span>
              Source type: <span className="font-medium text-gray-700">{viewingExtraction.extracted_data.source_type}</span>
            </span>
            <span>
              Slide count: <span className="font-medium text-gray-700">{viewingExtraction.extracted_data.metadata?.slide_count as number ?? "—"}</span>
            </span>
            {viewingExtraction.extracted_at && (
              <span>
                Extracted at: <span className="font-medium text-gray-700">{new Date(viewingExtraction.extracted_at).toLocaleString()}</span>
              </span>
            )}
          </div>

          {/* Slides */}
          <div className="space-y-4">
            {viewingExtraction.extracted_data.slides?.map((slide) => (
              <div key={slide.slide_number} className="rounded-md border border-gray-200 p-4">
                <div className="mb-2 flex items-center gap-3">
                  <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">
                    Slide {slide.slide_number}
                  </span>
                  {slide.title && (
                    <span className="text-sm font-medium text-gray-900">
                      {slide.title}
                    </span>
                  )}
                </div>

                {/* Text blocks */}
                {slide.texts.length > 0 && (
                  <div className="mb-2">
                    <div className="mb-1 text-xs font-medium uppercase text-gray-400">Text Blocks</div>
                    <ul className="list-inside list-disc space-y-1 text-sm text-gray-700">
                      {slide.texts.map((text, idx) => (
                        <li key={idx}>{text}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Tables */}
                {slide.tables.length > 0 && (
                  <div className="mb-2">
                    <div className="mb-1 text-xs font-medium uppercase text-gray-400">Tables</div>
                    {slide.tables.map((table, tIdx) => (
                      <table key={tIdx} className="mb-2 border-collapse border border-gray-300 text-xs">
                        <tbody>
                          {table.map((row, rIdx) => (
                            <tr key={rIdx}>
                              {row.map((cell, cIdx) => (
                                <td key={cIdx} className="border border-gray-300 px-2 py-1 text-gray-700">
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ))}
                  </div>
                )}

                {/* Speaker notes */}
                {slide.notes && (
                  <div className="mb-2">
                    <div className="mb-1 text-xs font-medium uppercase text-gray-400">Speaker Notes</div>
                    <p className="text-sm text-gray-600 italic">{slide.notes}</p>
                  </div>
                )}

                {/* Empty slide */}
                {slide.texts.length === 0 && slide.tables.length === 0 && !slide.notes && !slide.title && (
                  <p className="text-sm text-gray-400 italic">No extractable content on this slide.</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Accepted file types hint */}
      <p className="mt-4 text-xs text-gray-400">
        Accepted file types: PPTX, PDF, DOCX, XLSX
      </p>
    </div>
  );
}
