import { apiRequest } from ".";

export interface Team {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export type TeamCreate = {
  name: string;
  description?: string;
};

export type TeamUpdate = Partial<TeamCreate>;

export const teamsApi = {
  list: () => apiRequest<Team[]>("/teams/", { auth: true }),

  get: (id: number) => apiRequest<Team>(`/teams/${id}`, { auth: true }),

  create: (data: TeamCreate) =>
    apiRequest<Team>("/teams/", {
      method: "POST",
      body: data,
      auth: true,
    }),

  update: (id: number, data: TeamUpdate) =>
    apiRequest<Team>(`/teams/${id}`, {
      method: "PUT",
      body: data,
      auth: true,
    }),

  delete: (id: number) =>
    apiRequest(`/teams/${id}`, {
      method: "DELETE",
      auth: true,
    }),

  members: (id: number) => apiRequest<any[]>(`/teams/${id}/members`, { auth: true }),
};
