const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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
  extracted_at: string | null;
}

export interface ExtractionSlide {
  slide_number: number;
  title: string | null;
  texts: string[];
  tables: string[][][];
  notes: string | null;
}

export interface ExtractionData {
  source_type: string;
  metadata: Record<string, unknown>;
  slides: ExtractionSlide[];
}

export interface ExtractionResponse {
  id: string;
  lesson_id: string;
  original_filename: string;
  file_type: string | null;
  processing_status: string;
  extracted_at: string | null;
  extracted_data: ExtractionData | null;
}

export interface CourseCurriculumSource {
  id: string;
  course_id: string;
  original_filename: string;
  file_type: string | null;
  storage_path: string;
  uploaded_at: string;
  processing_status: string;
  extracted_at: string | null;
}

export interface CourseExtractionResponse {
  id: string;
  course_id: string;
  original_filename: string;
  file_type: string | null;
  processing_status: string;
  extracted_at: string | null;
  extracted_data: ExtractionData | null;
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

  extractCurriculum: (curriculumId: string) =>
    request<ExtractionResponse>(`/api/curriculum/${curriculumId}/extract`, {
      method: "POST",
    }),

  getExtraction: (curriculumId: string) =>
    request<ExtractionResponse>(`/api/curriculum/${curriculumId}/extraction`),

  // Course-level Curriculum
  listCourseCurriculum: (courseId: string) =>
    request<CourseCurriculumSource[]>(`/api/courses/${courseId}/curriculum`),

  uploadCourseCurriculum: async (
    courseId: string,
    files: File[],
  ): Promise<CourseCurriculumSource[]> => {
    const url = `${API_URL}/api/courses/${courseId}/curriculum`;
    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }

    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`API error ${res.status}: ${body}`);
    }

    return res.json() as Promise<CourseCurriculumSource[]>;
  },

  extractCourseCurriculum: (sourceId: string) =>
    request<CourseExtractionResponse>(
      `/api/course-curriculum/${sourceId}/extract`,
      { method: "POST" },
    ),

  getCourseExtraction: (sourceId: string) =>
    request<CourseExtractionResponse>(
      `/api/course-curriculum/${sourceId}/extraction`,
    ),
};
