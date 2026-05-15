import { apiRequest } from ".";

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  progress: number;
  start_date?: string;
  due_date?: string;
  team_id: number;
  team_name?: string;
  created_at: string;
  updated_at: string;
}

export type ProjectCreate = {
  name: string;
  description?: string;
  status?: string;
  progress?: number;
  start_date?: string;
  due_date?: string;
  team_id: number;
};

export type ProjectUpdate = Partial<ProjectCreate>;

export const projectsApi = {
  list: (teamId?: number) => {
    const query = teamId ? `?team_id=${teamId}` : "";
    return apiRequest<Project[]>(`/projects/${query}`, { auth: true });
  },

  get: (id: number) => apiRequest<Project>(`/projects/${id}`, { auth: true }),

  create: (data: ProjectCreate) =>
    apiRequest<Project>("/projects/", {
      method: "POST",
      body: data,
      auth: true,
    }),

  update: (id: number, data: ProjectUpdate) =>
    apiRequest<Project>(`/projects/${id}`, {
      method: "PUT",
      body: data,
      auth: true,
    }),

  delete: (id: number) =>
    apiRequest(`/projects/${id}`, {
      method: "DELETE",
      auth: true,
    }),
};
