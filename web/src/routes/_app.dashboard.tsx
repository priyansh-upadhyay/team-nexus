import { createFileRoute, Link } from '@tanstack/react-router'
import { useAuth } from "@/hooks/use-auth";
import { tasksApi } from "@/lib/api/tasks";
import { projectsApi } from "@/lib/api/projects";
import { teamsApi } from "@/lib/api/teams";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { FolderKanban, Clock, CheckCircle2, Users, TrendingUp, ArrowUpRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { PriorityBadge } from "@/components/PriorityBadge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_app/dashboard")({
  head: () => ({ meta: [{ title: "Dashboard — Team Nexus" }] }),
  component: Dashboard,
});

function Dashboard() {
  const { user } = useAuth();
  
  const { data: tasks } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => tasksApi.list(),
  });

  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectsApi.list(),
  });

  const { data: teams } = useQuery({
    queryKey: ["teams"],
    queryFn: () => teamsApi.list(),
  });

  const openTasks = tasks?.filter(t => t.status.toLowerCase() !== "done").length || 0;
  const completedTasks = tasks?.filter(t => t.status.toLowerCase() === "done").length || 0;
  const activeProjects = projects?.length || 0;
  const teamCount = teams?.length || 0;

  const stats = [
    { label: "Active projects", value: activeProjects.toString(), change: "+0", icon: FolderKanban },
    { label: "Open tasks", value: openTasks.toString(), change: "-0", icon: Clock },
    { label: "Completed tasks", value: completedTasks.toString(), change: "+0", icon: CheckCircle2 },
    { label: "Total teams", value: teamCount.toString(), change: "+0", icon: Users },
  ];

  const recentTasks = tasks?.slice(0, 5) || [];

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="space-y-8">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <p className="text-sm text-muted-foreground uppercase tracking-wider font-medium">
            {format(new Date(), "EEEE, MMMM d")}
          </p>
          <h1 className="text-3xl font-semibold tracking-tight mt-1 text-foreground">
            {greeting}
          </h1>
        </div>
        <div className="text-sm text-muted-foreground flex items-center gap-2 bg-secondary/50 px-3 py-1.5 rounded-full border border-border">
          <TrendingUp className="h-4 w-4 text-success" />
          System healthy and operational
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <Card key={s.label} className="p-5 rounded-2xl border border-border bg-card shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center justify-between">
              <s.icon className="h-5 w-5 text-primary/80" />
              <span className="text-[10px] font-bold text-success bg-success/10 px-1.5 py-0.5 rounded uppercase">{s.change}</span>
            </div>
            <p className="text-3xl font-bold mt-3 text-foreground tracking-tight">{s.value}</p>
            <p className="text-xs font-medium text-muted-foreground mt-1 uppercase tracking-wider">{s.label}</p>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="p-6 rounded-2xl border border-border bg-card lg:col-span-2 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold text-foreground">Recent tasks</h2>
            <Link to="/tasks" className="text-xs font-medium text-primary hover:underline inline-flex items-center gap-1">
              View all <ArrowUpRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="space-y-1">
            {recentTasks.length > 0 ? (
              recentTasks.map((t) => (
                <div key={t.id} className="flex items-center gap-4 p-3 rounded-xl hover:bg-muted/50 transition-colors border border-transparent hover:border-border/50">
                  <span className="text-[10px] text-muted-foreground font-mono w-12">#{t.id}</span>
                  <p className="flex-1 text-sm font-medium text-foreground truncate">{t.title}</p>
                  <PriorityBadge priority={t.priority as any} />
                  <span className="text-[10px] font-medium text-muted-foreground w-20 text-right">
                    {t.due_date ? (
                      (() => {
                        try {
                          return format(new Date(t.due_date), "MMM d");
                        } catch (e) {
                          return "Soon";
                        }
                      })()
                    ) : "Soon"}
                  </span>
                  <Avatar className="h-7 w-7 border-2 border-background">
                    <AvatarFallback className="text-[10px] bg-primary/10 text-primary font-bold">
                      {t.assignee_id ? `U${t.assignee_id}` : "?"}
                    </AvatarFallback>
                  </Avatar>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground py-10 text-center">No tasks found yet.</p>
            )}
          </div>
        </Card>

        <Card className="p-6 rounded-2xl border border-border bg-card shadow-sm">
          <h2 className="font-semibold text-foreground mb-5">Projects list</h2>
          <div className="space-y-4">
            {projects && projects.length > 0 ? (
                projects.slice(0, 5).map((p) => {
                  const progress = p.progress || 0;

                  return (
                    <Link key={p.id} to="/projects/$projectId" params={{ projectId: p.id.toString() }} className="group block">
                      <div className="flex justify-between text-sm mb-2 items-center">
                        <span className="font-medium text-foreground group-hover:text-primary transition-colors">{p.name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-muted-foreground font-bold">{progress}%</span>
                          <span className="text-[10px] font-bold text-muted-foreground uppercase bg-muted px-1.5 py-0.5 rounded">{p.status}</span>
                        </div>
                      </div>
                      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                        <div 
                          className="h-full bg-primary/80 transition-all duration-500" 
                          style={{ width: `${progress}%` }} 
                        /> 
                      </div>
                    </Link>
                  )
                })
            ) : (
              <p className="text-sm text-muted-foreground py-10 text-center">No projects created yet.</p>
            )}
            <Button variant="outline" className="w-full text-xs h-9 mt-2" asChild>
              <Link to="/projects">All projects</Link>
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
