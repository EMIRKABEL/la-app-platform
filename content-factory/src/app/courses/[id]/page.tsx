"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  api,
  Course,
  Unit,
  Lesson,
  CourseCurriculumSource,
  CourseExtractionResponse,
} from "@/lib/api";

const ACCEPTED_EXTENSIONS = ".pptx,.pdf,.docx,.xlsx";

export default function CourseDetailPage() {
  const params = useParams();
  const courseId = params.id as string;

  const [course, setCourse] = useState<Course | null>(null);
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Course curriculum state
  const [courseCurriculum, setCourseCurriculum] = useState<CourseCurriculumSource[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [courseSuccess, setCourseSuccess] = useState<string | null>(null);
  const courseFileInputRef = useRef<HTMLInputElement>(null);

  // Extraction state
  const [extractingId, setExtractingId] = useState<string | null>(null);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [extractionSuccess, setExtractionSuccess] = useState<string | null>(null);
  const [viewingExtraction, setViewingExtraction] = useState<CourseExtractionResponse | null>(null);
  const [viewingExtractionLoading, setViewingExtractionLoading] = useState(false);

  // New unit form state
  const [showUnitForm, setShowUnitForm] = useState(false);
  const [unitNumber, setUnitNumber] = useState("");
  const [unitTitle, setUnitTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Expanded unit → lessons
  const [expandedUnitId, setExpandedUnitId] = useState<string | null>(null);
  const [unitLessons, setUnitLessons] = useState<Lesson[]>([]);
  const [lessonsLoading, setLessonsLoading] = useState(false);

  // New lesson form
  const [showLessonForm, setShowLessonForm] = useState(false);
  const [lessonNumber, setLessonNumber] = useState("");
  const [lessonTitle, setLessonTitle] = useState("");
  const [lessonSubmitting, setLessonSubmitting] = useState(false);

  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [c, u, cc] = await Promise.all([
        api.getCourse(courseId),
        api.listUnits(courseId),
        api.listCourseCurriculum(courseId),
      ]);
      setCourse(c);
      setUnits(u);
      setCourseCurriculum(cc);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load course");
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const refreshCourseCurriculum = useCallback(async () => {
    try {
      const cc = await api.listCourseCurriculum(courseId);
      setCourseCurriculum(cc);
    } catch {
      // ignore
    }
  }, [courseId]);

  // ── Course curriculum handlers ──────────────────────────────

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
      setUploadError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadError(null);
    setCourseSuccess(null);

    try {
      const records = await api.uploadCourseCurriculum(courseId, selectedFiles);
      const skipped = selectedFiles.length - records.length;
      if (skipped > 0) {
        setCourseSuccess(
          `${records.length} file(s) uploaded. ${skipped} unsupported file(s) skipped.`,
        );
      } else {
        setCourseSuccess(`${records.length} file(s) uploaded successfully.`);
      }
      setSelectedFiles([]);
      if (courseFileInputRef.current) {
        courseFileInputRef.current.value = "";
      }
      setTimeout(() => setCourseSuccess(null), 5000);
      await refreshCourseCurriculum();
    } catch (err) {
      setUploadError(
        err instanceof Error ? err.message : "Failed to upload files",
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
      const result = await api.extractCourseCurriculum(sourceId);
      setExtractionSuccess(
        `Extraction complete: ${result.extracted_data?.metadata?.slide_count as number ?? 0} slides extracted.`,
      );
      setTimeout(() => setExtractionSuccess(null), 5000);
      await refreshCourseCurriculum();
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
      const result = await api.getCourseExtraction(sourceId);
      setViewingExtraction(result);
    } catch (err) {
      setExtractionError(
        err instanceof Error ? err.message : "Failed to load extraction",
      );
    } finally {
      setViewingExtractionLoading(false);
    }
  };

  // ── Unit/Lesson handlers ─────────────────────────────────────

  const handleCreateUnit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const unit = await api.createUnit(courseId, {
        number: parseInt(unitNumber, 10),
        title: unitTitle.trim(),
      });
      setUnits((prev) => [...prev, unit].sort((a, b) => a.number - b.number));
      setUnitNumber("");
      setUnitTitle("");
      setShowUnitForm(false);
      setSuccessMessage(`Unit "${unit.title}" created successfully.`);
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create unit");
    } finally {
      setSubmitting(false);
    }
  };

  const loadLessons = useCallback(async (unitId: string) => {
    setLessonsLoading(true);
    try {
      const lessons = await api.listLessons(unitId);
      setUnitLessons(lessons);
    } catch {
      setUnitLessons([]);
    } finally {
      setLessonsLoading(false);
    }
  }, []);

  const handleUnitClick = (unitId: string) => {
    if (expandedUnitId === unitId) {
      setExpandedUnitId(null);
      setUnitLessons([]);
      setShowLessonForm(false);
    } else {
      setExpandedUnitId(unitId);
      setShowLessonForm(false);
      loadLessons(unitId);
    }
  };

  const handleCreateLesson = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!expandedUnitId) return;
    setLessonSubmitting(true);
    setError(null);
    try {
      const lesson = await api.createLesson(expandedUnitId, {
        number: parseInt(lessonNumber, 10),
        title: lessonTitle.trim(),
      });
      setUnitLessons((prev) =>
        [...prev, lesson].sort((a, b) => a.number - b.number),
      );
      setLessonNumber("");
      setLessonTitle("");
      setShowLessonForm(false);
      setSuccessMessage(`Lesson "${lesson.title}" created successfully.`);
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create lesson");
    } finally {
      setLessonSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-gray-500">Loading course...</div>;
  }

  if (error && !course) {
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
        <Link href="/courses" className="hover:text-indigo-600">
          Courses
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-700">{course?.name}</span>
      </nav>

      {/* Course info */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{course?.name}</h1>
        {course?.description && (
          <p className="mt-1 text-gray-600">{course.description}</p>
        )}
      </div>

      {/* Course Curriculum section */}
      <div className="mb-8">
        <h2 className="mb-3 border-b border-gray-200 pb-2 text-lg font-bold text-gray-900">
          Course Curriculum
        </h2>

        {courseSuccess && (
          <div className="mb-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {courseSuccess}
          </div>
        )}
        {extractionSuccess && (
          <div className="mb-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
            {extractionSuccess}
          </div>
        )}

        {/* Upload bar */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Upload curriculum files for the entire course.
          </p>
          <button
            onClick={() => courseFileInputRef.current?.click()}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
          >
            Upload Curriculum
          </button>
        </div>

        {/* Upload form */}
        <form onSubmit={handleUpload} className="mb-6">
          <input
            ref={courseFileInputRef}
            type="file"
            accept={ACCEPTED_EXTENSIONS}
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />
          {selectedFiles.length > 0 && (
            <div className="mb-3 rounded-md border border-gray-200 bg-white px-4 py-3 shadow-sm">
              <div className="mb-2 text-sm font-medium text-gray-700">
                Selected files ({selectedFiles.length}):
              </div>
              <ul className="mb-3 space-y-1 text-sm text-gray-600">
                {selectedFiles.map((f, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="font-medium">{f.name}</span>
                    <span className="text-xs text-gray-400">
                      ({(f.size / 1024).toFixed(1)} KB)
                    </span>
                  </li>
                ))}
              </ul>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={uploading}
                  className="rounded-md bg-green-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50"
                >
                  {uploading ? "Uploading..." : "Confirm Upload"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFiles([]);
                    if (courseFileInputRef.current) {
                      courseFileInputRef.current.value = "";
                    }
                  }}
                  className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
          {uploading && (
            <div className="mb-3 text-sm text-gray-500">Uploading files...</div>
          )}
          {uploadError && (
            <div className="mb-3 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
              {uploadError}
            </div>
          )}
        </form>

        {/* Curriculum table */}
        {courseCurriculum.length === 0 && !uploading && (
          <p className="text-gray-500">
            No curriculum files uploaded yet.
          </p>
        )}

        {courseCurriculum.length > 0 && (
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
              {courseCurriculum.map((src) => (
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
                  {slide.notes && (
                    <div className="mb-2">
                      <div className="mb-1 text-xs font-medium uppercase text-gray-400">Speaker Notes</div>
                      <p className="text-sm text-gray-600 italic">{slide.notes}</p>
                    </div>
                  )}
                  {slide.texts.length === 0 && slide.tables.length === 0 && !slide.notes && !slide.title && (
                    <p className="text-sm text-gray-400 italic">No extractable content on this slide.</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="mt-4 text-xs text-gray-400">
          Accepted file types: PPTX, PDF, DOCX, XLSX — Multiple files can be selected at once.
        </p>
      </div>

      {/* Divider */}
      <hr className="mb-8 border-gray-200" />

      {/* Units section */}
      {successMessage && (
        <div className="mb-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
          {successMessage}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Units</h2>
        <button
          onClick={() => setShowUnitForm((s) => !s)}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          {showUnitForm ? "Cancel" : "New Unit"}
        </button>
      </div>

      {showUnitForm && (
        <form
          onSubmit={handleCreateUnit}
          className="mb-6 max-w-lg rounded-md border border-gray-200 bg-white p-6 shadow-sm"
        >
          <h3 className="text-base font-semibold">Create New Unit</h3>
          <div className="mt-4 space-y-4">
            <div>
              <label htmlFor="unit-number" className="block text-sm font-medium text-gray-700">
                Unit Number
              </label>
              <input
                id="unit-number"
                type="number"
                value={unitNumber}
                onChange={(e) => setUnitNumber(e.target.value)}
                required
                min={1}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                placeholder="e.g. 1"
              />
            </div>
            <div>
              <label htmlFor="unit-title" className="block text-sm font-medium text-gray-700">
                Unit Title
              </label>
              <input
                id="unit-title"
                type="text"
                value={unitTitle}
                onChange={(e) => setUnitTitle(e.target.value)}
                required
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                placeholder="e.g. Introduction to Grammar"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {submitting ? "Creating..." : "Create Unit"}
            </button>
          </div>
        </form>
      )}

      {units.length === 0 && !showUnitForm && (
        <p className="text-gray-500">No units yet. Click &quot;New Unit&quot; to create one.</p>
      )}

      {units.length > 0 && (
        <div className="space-y-2">
          {units.map((unit) => (
            <div key={unit.id} className="rounded-md border border-gray-200 bg-white shadow-sm">
              <div
                onClick={() => handleUnitClick(unit.id)}
                className="flex cursor-pointer items-center justify-between px-4 py-3 hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
                    {unit.number}
                  </span>
                  <span className="font-medium text-gray-900">{unit.title}</span>
                </div>
                <span className="text-sm text-gray-400">
                  {expandedUnitId === unit.id ? "▲" : "▼"}
                </span>
              </div>

              {expandedUnitId === unit.id && (
                <div className="border-t border-gray-100 px-4 py-3">
                  {lessonsLoading && (
                    <p className="text-sm text-gray-500">Loading lessons...</p>
                  )}

                  {!lessonsLoading && unitLessons.length === 0 && !showLessonForm && (
                    <p className="text-sm text-gray-500">
                      No lessons yet.
                    </p>
                  )}

                  {!lessonsLoading && unitLessons.length > 0 && (
                    <ul className="space-y-1">
                      {unitLessons.map((lesson) => (
                        <li key={lesson.id}>
                          <Link
                            href={`/lessons/${lesson.id}`}
                            className="flex items-center gap-2 rounded px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                          >
                            <span className="font-medium text-indigo-600">
                              Lesson {lesson.number}
                            </span>
                            <span>{lesson.title}</span>
                            <span className="ml-2 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                              {lesson.status}
                            </span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}

                  {/* New Lesson form */}
                  <div className="mt-3">
                    {!showLessonForm ? (
                      <button
                        onClick={() => setShowLessonForm(true)}
                        className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
                      >
                        + New Lesson
                      </button>
                    ) : (
                      <form
                        onSubmit={handleCreateLesson}
                        className="max-w-md rounded-md border border-gray-200 p-4"
                      >
                        <div className="space-y-3">
                          <div>
                            <label htmlFor="lesson-number" className="block text-sm font-medium text-gray-700">
                              Lesson Number
                            </label>
                            <input
                              id="lesson-number"
                              type="number"
                              value={lessonNumber}
                              onChange={(e) => setLessonNumber(e.target.value)}
                              required
                              min={1}
                              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                              placeholder="e.g. 1"
                            />
                          </div>
                          <div>
                            <label htmlFor="lesson-title" className="block text-sm font-medium text-gray-700">
                              Lesson Title
                            </label>
                            <input
                              id="lesson-title"
                              type="text"
                              value={lessonTitle}
                              onChange={(e) => setLessonTitle(e.target.value)}
                              required
                              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                              placeholder="e.g. Greetings"
                            />
                          </div>
                          <div className="flex gap-2">
                            <button
                              type="submit"
                              disabled={lessonSubmitting}
                              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                            >
                              {lessonSubmitting ? "Creating..." : "Create Lesson"}
                            </button>
                            <button
                              type="button"
                              onClick={() => setShowLessonForm(false)}
                              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      </form>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
