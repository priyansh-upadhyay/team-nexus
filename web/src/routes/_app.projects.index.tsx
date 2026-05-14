import { useState } from "react";
import { createFileRoute, Link } from '@tanstack/react-router'
import { projectsApi } from "@/lib/api/projects";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, AlertCircle, Users as UsersIcon, Calendar, Search, MoreHorizontal, Pencil, Trash } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CreateProjectDialog } from "@/components/projects/CreateProjectDialog";
import { EditProjectDialog } from "@/components/projects/EditProjectDialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { toast } from "sonner";

export const Route = createFileRoute("/_app/projects/")({
  head: () => ({ meta: [{ title: "Projects — Team Nexus" }] }),
  component: ProjectsPage,
});

function ProjectsPage() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [editingProject, setEditingProject] = useState<{ id: number; name: string; description: string | null } | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectsApi.list(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete project");
    }
  });

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <p className="text-sm font-medium text-foreground">Failed to load projects</p>
      </div>
    );
  }

  const filteredProjects = projects?.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">Projects</h1>
          <p className="text-sm text-muted-foreground mt-1">All active initiatives across your workspace.</p>
        </div>
        <CreateProjectDialog />
      </div>

      <div className="relative max-w-sm">
        <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <Input 
          placeholder="Search projects" 
          className="pl-9 bg-card" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredProjects.length > 0 ? (
          filteredProjects.map((p) => (
            <Link key={p.id} to="/projects/$projectId" params={{ projectId: p.id.toString() }}>
              <Card className="rounded-2xl p-6 hover:shadow-md transition-all border border-border bg-card h-full group">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="font-semibold tracking-tight truncate text-foreground group-hover:text-primary transition-colors">{p.name}</h3>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2 leading-relaxed">{p.description || "No description provided."}</p>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button 
                          size="icon" 
                          variant="ghost" 
                          className="h-8 w-8 text-muted-foreground hover:bg-muted" 
                          onClick={(e) => { 
                            e.preventDefault(); 
                            e.stopPropagation(); 
                          }}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="rounded-xl shadow-xl border-border min-w-[120px]">
                        <DropdownMenuItem onClick={(e) => { 
                          e.preventDefault(); 
                          e.stopPropagation();
                          setEditingProject(p);
                          setIsEditDialogOpen(true);
                        }}>
                          <Pencil className="h-4 w-4 mr-2" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem 
                          className="text-destructive focus:text-destructive focus:bg-destructive/10"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            if (confirm(`Are you sure you want to delete "${p.name}"?`)) {
                              deleteMutation.mutate(p.id);
                            }
                          }}
                        >
                          <Trash className="h-4 w-4 mr-2" /> Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                    <span className="text-[10px] font-bold text-muted-foreground uppercase bg-muted px-1.5 py-0.5 rounded">{p.status}</span>
                  </div>
                </div>

                <div className="mt-6 space-y-2">
                  <div className="flex items-center justify-between text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                    <span>Progress</span>
                    <span className="text-primary">{p.progress}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div 
                      className="h-full bg-primary/80 transition-all duration-500 shadow-[0_0_10px_rgba(var(--primary),0.3)]" 
                      style={{ width: `${p.progress}%` }} 
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between mt-6 text-[10px] font-medium text-muted-foreground uppercase tracking-widest">
                  <span className="inline-flex items-center gap-1.5 bg-secondary/50 px-2 py-0.5 rounded-full"><UsersIcon className="h-3 w-3" /> Team {p.team_id}</span>
                  <span className="inline-flex items-center gap-1.5">
                    <Calendar className="h-3 w-3" /> 
                    {p.start_date 
                      ? new Date(p.start_date).toLocaleDateString() 
                      : (p.created_at ? new Date(p.created_at).toLocaleDateString() : "New")
                    }
                  </span>
                </div>
              </Card>
            </Link>
          ))
        ) : (
          <div className="col-span-full py-20 text-center border border-dashed border-border rounded-2xl bg-muted/20">
            <p className="text-muted-foreground">No projects found. Create your first project to get started.</p>
          </div>
        )}
      </div>
      {editingProject && (
        <EditProjectDialog 
          project={editingProject} 
          open={isEditDialogOpen} 
          onOpenChange={setIsEditDialogOpen} 
        />
      )}
    </div>
  );
}
