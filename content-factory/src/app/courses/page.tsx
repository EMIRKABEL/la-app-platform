"use client";

import { useCallback, useEffect, useState } from "react";
import { api, Course } from "@/lib/api";
import { NewCourseForm } from "@/components/NewCourseForm";

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const loadCourses = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listCourses();
      setCourses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load courses");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  const handleCreated = (course: Course) => {
    setCourses((prev) => [course, ...prev]);
    setShowForm(false);
    setSuccessMessage(`Course "${course.name}" created successfully.`);
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Courses</h1>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          {showForm ? "Cancel" : "New Course"}
        </button>
      </div>

      {successMessage && (
        <div className="mt-4 rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
          {successMessage}
        </div>
      )}

      {showForm && (
        <div className="mt-6">
          <NewCourseForm onCreated={handleCreated} />
        </div>
      )}

      {loading && (
        <div className="mt-8 text-gray-500">Loading courses...</div>
      )}

      {error && (
        <div className="mt-8 rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && courses.length === 0 && (
        <div className="mt-8 text-gray-500">
          No courses yet. Click &quot;New Course&quot; to create one.
        </div>
      )}

      {!loading && !error && courses.length > 0 && (
        <table className="mt-6 w-full border-collapse">
          <thead>
            <tr className="border-b border-gray-200 text-left text-sm text-gray-500">
              <th className="py-3 pr-4 font-medium">Name</th>
              <th className="py-3 pr-4 font-medium">Description</th>
              <th className="py-3 pr-4 font-medium">Created</th>
            </tr>
          </thead>
          <tbody>
            {courses.map((course) => (
              <tr
                key={course.id}
                className="border-b border-gray-100 text-sm"
              >
                <td className="py-3 pr-4 font-medium text-gray-900">
                  {course.name}
                </td>
                <td className="py-3 pr-4 text-gray-600">
                  {course.description || "—"}
                </td>
                <td className="py-3 pr-4 text-gray-500">
                  {new Date(course.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
