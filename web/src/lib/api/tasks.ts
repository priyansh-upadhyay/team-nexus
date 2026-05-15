import { apiRequest } from ".";

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  due_date?: string;
  project_id?: number;
  assignee_id?: number;
  created_at: string;
  updated_at: string;
}

export type TaskCreate = {
  title: string;
  description?: string;
  status?: string;
  priority?: string;
  due_date?: string;
  project_id?: number;
  assignee_id?: number;
};

export type TaskUpdate = Partial<TaskCreate>;

export const tasksApi = {
  list: (params?: { project_id?: number; assignee_id?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.project_id) searchParams.append("project_id", params.project_id.toString());
    if (params?.assignee_id) searchParams.append("assignee_id", params.assignee_id.toString());
    const query = searchParams.toString() ? `?${searchParams.toString()}` : "";
    return apiRequest<Task[]>(`/tasks/${query}`, { auth: true });
  },

  get: (id: number) => apiRequest<Task>(`/tasks/${id}`, { auth: true }),

  create: (data: TaskCreate) =>
    apiRequest<Task>("/tasks/", {
      method: "POST",
      body: data,
      auth: true,
    }),

  update: (id: number, data: TaskUpdate) =>
    apiRequest<Task>(`/tasks/${id}`, {
      method: "PUT",
      body: data,
      auth: true,
    }),

  delete: (id: number) =>
    apiRequest(`/tasks/${id}`, {
      method: "DELETE",
      auth: true,
    }),
};
