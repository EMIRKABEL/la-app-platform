"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api, Course, Unit, Lesson } from "@/lib/api";

export default function CourseDetailPage() {
  const params = useParams();
  const courseId = params.id as string;

  const [course, setCourse] = useState<Course | null>(null);
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      const [c, u] = await Promise.all([
        api.getCourse(courseId),
        api.listUnits(courseId),
      ]);
      setCourse(c);
      setUnits(u);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load course");
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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

      {/* Units section */}
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
