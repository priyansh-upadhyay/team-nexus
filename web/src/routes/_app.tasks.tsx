import { useState } from "react";
import { createFileRoute } from '@tanstack/react-router'
import { tasksApi } from "@/lib/api/tasks";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, AlertCircle, Search, Filter, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { PriorityBadge } from "@/components/PriorityBadge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { CreateTaskDialog } from "@/components/tasks/CreateTaskDialog";

export const Route = createFileRoute("/_app/tasks")({
  head: () => ({ meta: [{ title: "Tasks — Team Nexus" }] }),
  component: TasksPage,
});

const statusStyles: Record<string, string> = {
  "Todo": "bg-muted text-muted-foreground",
  "In Progress": "bg-info/15 text-info",
  "Review": "bg-warning/15 text-warning",
  "Done": "bg-success/15 text-success",
};

function TasksPage() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const { data: tasks, isLoading, error } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksApi.list(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => tasksApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
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
        <p className="text-sm font-medium text-foreground">Failed to load tasks</p>
      </div>
    );
  }

  const filteredTasks = tasks?.filter(t => 
    t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.id.toString().includes(searchTerm)
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">Tasks</h1>
          <p className="text-sm text-muted-foreground mt-1">Every task assigned across projects.</p>
        </div>
        <CreateTaskDialog />
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input 
            placeholder="Search tasks" 
            className="pl-9 bg-card border border-border shadow-sm"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <Card className="rounded-2xl overflow-hidden border border-border bg-card shadow-sm">
        <div className="grid grid-cols-12 px-5 py-4 text-[10px] font-bold uppercase tracking-widest text-muted-foreground border-b border-border bg-muted/30">
          <div className="col-span-1">ID</div>
          <div className="col-span-4">Title</div>
          <div className="col-span-2 text-center">Project ID</div>
          <div className="col-span-1 text-center">Priority</div>
          <div className="col-span-1 text-center">Status</div>
          <div className="col-span-1 text-center">Due</div>
          <div className="col-span-1 text-center">Assignee</div>
          <div className="col-span-1 text-right">Action</div>
        </div>
        <div className="divide-y divide-border">
          {filteredTasks.length > 0 ? (
            filteredTasks.map((t) => (
              <div key={t.id} className="grid grid-cols-12 items-center px-5 py-3.5 text-sm hover:bg-muted/30 transition-colors">
                <div className="col-span-1 font-mono text-[10px] text-muted-foreground">#{t.id}</div>
                <div className="col-span-4 truncate font-medium text-foreground">{t.title}</div>
                <div className="col-span-2 text-muted-foreground text-xs text-center">{t.project_id || "-"}</div>
                <div className="col-span-1 flex justify-center"><PriorityBadge priority={t.priority as any} /></div>
                <div className="col-span-1 flex justify-center">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${statusStyles[t.status] || "bg-muted"}`}>{t.status}</span>
                </div>
                <div className="col-span-1 text-muted-foreground text-[10px] text-center font-medium">{t.due_date ? new Date(t.due_date).toLocaleDateString() : "-"}</div>
                <div className="col-span-1 flex justify-center">
                  <Avatar className="h-7 w-7 border border-background shadow-sm">
                    <AvatarFallback className="text-[10px] bg-primary/10 text-primary font-bold">
                      {t.assignee_id ? `U${t.assignee_id}` : "?"}
                    </AvatarFallback>
                  </Avatar>
                </div>
                <div className="col-span-1 flex justify-end">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                    onClick={() => {
                      if (confirm("Are you sure you want to delete this task?")) {
                        deleteMutation.mutate(t.id);
                      }
                    }}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending && deleteMutation.variables === t.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <div className="py-20 text-center">
              <p className="text-muted-foreground text-sm font-medium">No tasks found.</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
