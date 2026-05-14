import { createFileRoute } from "@tanstack/react-router";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Plus, Calendar, MoreHorizontal, Filter, Loader2, AlertCircle } from "lucide-react";
import { PriorityBadge } from "@/components/PriorityBadge";
import { tasksApi, type Task } from "@/lib/api/tasks";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CreateTaskDialog } from "@/components/tasks/CreateTaskDialog";
import { ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/kanban")({
  head: () => ({ meta: [{ title: "Task Board — Team Nexus" }] }),
  component: KanbanPage,
});

const columns: { id: string; status: string; accent: string; hint: string }[] = [
  { id: "todo", status: "Todo", accent: "bg-muted-foreground/60", hint: "Backlog & ready to start" },
  { id: "in_progress", status: "In Progress", accent: "bg-info", hint: "Actively being worked on" },
  { id: "review", status: "Review", accent: "bg-warning", hint: "Awaiting feedback" },
  { id: "done", status: "Done", accent: "bg-success", hint: "Shipped this cycle" },
];


function TaskCard({ t }: { t: Task }) {
  const queryClient = useQueryClient();
  const userInitials = t.assignee_id ? `U${t.assignee_id}` : "?";
  
  const moveMutation = useMutation({
    mutationFn: (newStatus: string) => tasksApi.update(t.id, { status: newStatus }),
    onMutate: async (newStatus) => {
      await queryClient.cancelQueries({ queryKey: ["tasks"] });
      const previousTasks = queryClient.getQueryData<Task[]>(["tasks"]);
      
      if (previousTasks) {
        queryClient.setQueryData<Task[]>(["tasks"], 
          previousTasks.map(task => 
            task.id === t.id ? { ...task, status: newStatus } : task
          )
        );
      }
      return { previousTasks };
    },
    onError: (err, newStatus, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(["tasks"], context.previousTasks);
      }
      toast.error("Failed to move task");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
    onSuccess: (_, newStatus) => {
      toast.success(`Task moved to ${columns.find(c => c.id === newStatus)?.status}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => tasksApi.delete(t.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task deleted");
    },
  });

  const currentIndex = columns.findIndex(c => c.id === t.status);

  return (
    <Card className="group bg-card border border-border rounded-xl p-4 space-y-3 shadow-sm hover:shadow-md hover:border-border/80 transition-all">
      <div className="flex items-start justify-between gap-2">
        <span className="text-[10px] font-mono text-muted-foreground tracking-wide">#{t.id}</span>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {currentIndex > 0 && (
            <Button 
              size="icon" variant="ghost" className="h-6 w-6" 
              onClick={() => moveMutation.mutate(columns[currentIndex - 1].id)}
            >
              <ChevronLeft className="h-3 w-3" />
            </Button>
          )}
          {currentIndex < columns.length - 1 && (
            <Button 
              size="icon" variant="ghost" className="h-6 w-6" 
              onClick={() => moveMutation.mutate(columns[currentIndex + 1].id)}
            >
              <ChevronRight className="h-3 w-3" />
            </Button>
          )}
          <Button 
            size="icon" variant="ghost" className="h-6 w-6 text-destructive hover:text-destructive hover:bg-destructive/10" 
            onClick={() => { if(confirm("Delete task?")) deleteMutation.mutate(); }}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>
      <div className="space-y-1.5">
        <p className="text-sm font-medium leading-snug text-foreground">{t.title}</p>
        <div className="flex items-center gap-2">
          <PriorityBadge priority={t.priority as any} />
        </div>
      </div>
      <div className="flex items-center justify-between pt-2 border-t border-border/60">
        <span className="inline-flex items-center gap-1.5 text-[10px] font-medium text-muted-foreground">
          <Calendar className="h-3 w-3" /> {t.due_date ? new Date(t.due_date).toLocaleDateString() : "No due date"}
        </span>
        <Avatar className="h-6 w-6 ring-2 ring-background">
          <AvatarFallback className="text-[10px] font-medium bg-primary/10 text-primary">
            {userInitials}
          </AvatarFallback>
        </Avatar>
      </div>
    </Card>
  );
}

function KanbanPage() {
  const queryClient = useQueryClient();
  const { data: tasks, isLoading, error } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksApi.list(),
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
        <p className="text-sm font-medium">Failed to load tasks</p>
        <Button variant="outline" size="sm" onClick={() => queryClient.invalidateQueries({ queryKey: ["tasks"] })}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Task board</h1>
          <p className="text-sm text-muted-foreground mt-1">Plan, prioritize, and ship across stages.</p>
        </div>
        <div className="flex items-center gap-2">
          <CreateTaskDialog />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 flex-1">
        {columns.map((col) => {
          const colTasks = tasks?.filter((t) => t.status === col.id) || [];
          return (
            <div
              key={col.id}
              className="bg-muted/30 border border-border/70 rounded-2xl p-3 flex flex-col min-h-[60vh]"
            >
              <div className="flex items-center justify-between px-2 py-1.5 mb-3">
                <div className="flex items-center gap-2">
                  <span className={`h-2 w-2 rounded-full ${col.accent}`} />
                  <h3 className="text-sm font-semibold text-foreground">{col.status}</h3>
                  <span className="text-xs font-medium text-muted-foreground bg-background border border-border rounded-md px-1.5 py-0.5 min-w-[22px] text-center">
                    {colTasks.length}
                  </span>
                </div>
              </div>
              <div className="space-y-2.5 flex-1 overflow-y-auto max-h-[70vh] pr-1 custom-scrollbar">
                {colTasks.map((t) => (
                  <TaskCard key={t.id} t={t} />
                ))}
                {colTasks.length === 0 && (
                  <div className="h-24 flex items-center justify-center border border-dashed border-border rounded-xl">
                    <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">No tasks</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
