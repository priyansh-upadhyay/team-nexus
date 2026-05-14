import { createFileRoute, Link } from '@tanstack/react-router'
import { projectsApi } from "@/lib/api/projects";
import { tasksApi } from "@/lib/api/tasks";
import { useQuery } from "@tanstack/react-query";
import { Loader2, AlertCircle, ArrowLeft, Calendar, CheckCircle2, Clock, MoreHorizontal, Pencil, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PriorityBadge } from "@/components/PriorityBadge";
import { CreateTaskDialog } from "@/components/tasks/CreateTaskDialog";
import { EditProjectDialog } from "@/components/projects/EditProjectDialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useState } from "react";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";

export const Route = createFileRoute("/_app/projects/$projectId")({
  head: () => ({ meta: [{ title: "Project Details — Team Nexus" }] }),
  component: ProjectDetailPage,
});

function ProjectDetailPage() {
  const { projectId } = Route.useParams();
  const id = parseInt(projectId);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ["project", id],
    queryFn: () => projectsApi.get(id),
  });

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ["tasks", "project", id],
    queryFn: () => tasksApi.list({ project_id: id }),
  });

  const deleteMutation = useMutation({
    mutationFn: () => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project deleted successfully");
      navigate({ to: "/projects" });
    },
    onError: () => {
      toast.error("Failed to delete project");
    }
  });

  if (projectLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <h2 className="text-xl font-semibold">Project not found</h2>
        <Button asChild variant="outline">
          <Link to="/projects">Back to projects</Link>
        </Button>
      </div>
    );
  }

  const progress = project.progress;

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/projects"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-semibold tracking-tight text-foreground">{project.name}</h1>
            <span className="text-[10px] font-bold text-muted-foreground uppercase bg-muted px-2 py-0.5 rounded">{project.status}</span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">{project.description || "No description provided."}</p>
        </div>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="rounded-xl shadow-xl border-border">
              <DropdownMenuItem onClick={() => setIsEditDialogOpen(true)}>
                <Pencil className="h-4 w-4 mr-2" /> Edit Project
              </DropdownMenuItem>
              <DropdownMenuItem 
                className="text-destructive focus:text-destructive focus:bg-destructive/10"
                onClick={() => {
                  if (confirm("Are you sure you want to delete this project?")) {
                    deleteMutation.mutate();
                  }
                }}
              >
                <Trash className="h-4 w-4 mr-2" /> Delete Project
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <CreateTaskDialog />
        </div>
      </div>

      <div className="grid sm:grid-cols-3 gap-6">
        <Card className="p-6 rounded-2xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <CheckCircle2 className="h-5 w-5 text-success/80" />
            <span className="text-2xl font-bold">{progress}%</span>
          </div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Completion</p>
          <div className="h-2 w-full bg-muted rounded-full mt-4 overflow-hidden">
            <div className="h-full bg-success transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
        </Card>
        
        <Card className="p-6 rounded-2xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <Clock className="h-5 w-5 text-primary/80" />
            <span className="text-2xl font-bold">{tasks?.length || 0}</span>
          </div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Total Tasks</p>
        </Card>
 
        <Card className="p-6 rounded-2xl border border-border bg-card shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <Calendar className="h-5 w-5 text-warning/80" />
            <span className="text-sm font-bold">
              {project.start_date 
                ? new Date(project.start_date).toLocaleDateString() 
                : (project.created_at ? new Date(project.created_at).toLocaleDateString() : "New")
              }
            </span>
          </div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Started on</p>
        </Card>
      </div>

      <EditProjectDialog 
        project={project} 
        open={isEditDialogOpen} 
        onOpenChange={setIsEditDialogOpen} 
      />

      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-foreground">Project Tasks</h2>
        <Card className="rounded-2xl overflow-hidden border border-border bg-card shadow-sm">
          {tasksLoading ? (
            <div className="p-12 flex justify-center"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : tasks && tasks.length > 0 ? (
            <div className="divide-y divide-border">
              {tasks.map((t) => (
                <div key={t.id} className="flex items-center gap-4 px-6 py-4 hover:bg-muted/30 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{t.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{t.description || "No description"}</p>
                  </div>
                  <PriorityBadge priority={t.priority as any} />
                  <span className="text-[10px] font-bold text-muted-foreground uppercase bg-muted px-2 py-0.5 rounded">{t.status}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-muted-foreground">
              <p>No tasks found for this project yet.</p>
              <Button variant="link" className="mt-2 text-primary">Create the first task</Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
