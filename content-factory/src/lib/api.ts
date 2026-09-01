const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────

export interface Course {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateCourseInput {
  name: string;
  description?: string;
}

export interface Unit {
  id: string;
  course_id: string;
  number: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface CreateUnitInput {
  number: number;
  title: string;
}

export interface Lesson {
  id: string;
  unit_id: string;
  number: number;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CreateLessonInput {
  number: number;
  title: string;
}

export interface CurriculumSource {
  id: string;
  lesson_id: string;
  original_filename: string;
  file_type: string | null;
  storage_path: string;
  uploaded_at: string;
  processing_status: string;
}

// ── Request helper ───────────────────────────────────────────────

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }

  // 204 No Content
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

// ── API methods ──────────────────────────────────────────────────

export const api = {
  // Courses
  listCourses: () =>
    request<Course[]>("/api/courses"),

  getCourse: (id: string) =>
    request<Course>(`/api/courses/${id}`),

  createCourse: (data: CreateCourseInput) =>
    request<Course>("/api/courses", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Units
  listUnits: (courseId: string) =>
    request<Unit[]>(`/api/courses/${courseId}/units`),

  createUnit: (courseId: string, data: CreateUnitInput) =>
    request<Unit>(`/api/courses/${courseId}/units`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getUnit: (unitId: string) =>
    request<Unit>(`/api/units/${unitId}`),

  // Lessons
  listLessons: (unitId: string) =>
    request<Lesson[]>(`/api/units/${unitId}/lessons`),

  createLesson: (unitId: string, data: CreateLessonInput) =>
    request<Lesson>(`/api/units/${unitId}/lessons`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getLesson: (lessonId: string) =>
    request<Lesson>(`/api/lessons/${lessonId}`),

  // Curriculum
  listCurriculum: (lessonId: string) =>
    request<CurriculumSource[]>(`/api/lessons/${lessonId}/curriculum`),

  uploadCurriculum: async (lessonId: string, file: File): Promise<CurriculumSource> => {
    const url = `${API_URL}/api/lessons/${lessonId}/curriculum`;
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(url, {
      method: "POST",
      body: formData,
      // Do NOT set Content-Type — the browser sets it with the boundary
    });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`API error ${res.status}: ${body}`);
    }

    return res.json() as Promise<CurriculumSource>;
  },
};
