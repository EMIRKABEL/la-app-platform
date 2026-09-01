const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

export const api = {
  listCourses: () =>
    request<Course[]>("/api/courses"),

  getCourse: (id: string) =>
    request<Course>(`/api/courses/${id}`),

  createCourse: (data: CreateCourseInput) =>
    request<Course>("/api/courses", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
