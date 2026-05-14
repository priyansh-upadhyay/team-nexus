import { Link, Outlet, useRouterState, useRouter } from "@tanstack/react-router";
import { useAuth } from "@/hooks/use-auth";
import { LayoutDashboard, Users, FolderKanban, CheckSquare, Columns3, Search, Bell, Settings, LogOut, Shield } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/teams", label: "Teams", icon: Users },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/tasks", label: "Tasks", icon: CheckSquare },
  { to: "/kanban", label: "Task Board", icon: Columns3 },
] as const;

import { projectsApi, type Project } from "@/lib/api/projects";
import { useQuery } from "@tanstack/react-query";
import { isAfter, isBefore, addDays, parseISO, format } from "date-fns";

export function AppLayout() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { user, logout } = useAuth();
  const router = useRouter();
  const [search, setSearch] = useState("");
  
  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectsApi.list(),
  });

  const [notifications, setNotifications] = useState<{ id: string; title: string; description: string; type: "system" | "deadline" }[]>([
    { id: "1", title: "Welcome to Team Nexus! 🚀", description: "Start by creating your first team and project.", type: "system" },
    { id: "2", title: "New feature available", description: "Global search is now enabled across the platform.", type: "system" },
  ]);

  // Generate deadline notifications
  useEffect(() => {
    if (projects) {
      const today = new Date();
      const in3Days = addDays(today, 3);
      
      const deadlineNotifs = projects
        .filter(p => p.due_date && !p.status.toLowerCase().includes("done"))
        .filter(p => {
          try {
            const dueDate = parseISO(p.due_date!);
            return isAfter(dueDate, today) && isBefore(dueDate, in3Days);
          } catch (e) {
            return false;
          }
        })
        .map(p => ({
          id: `p-${p.id}`,
          title: `Deadline approaching: ${p.name}`,
          description: `Due on ${format(parseISO(p.due_date!), "MMM d, yyyy")}`,
          type: "deadline" as const
        }));

      setNotifications(prev => {
        const existingIds = new Set(prev.map(n => n.id));
        const newNotifs = deadlineNotifs.filter(n => !existingIds.has(n.id));
        if (newNotifs.length === 0) return prev;
        return [...prev, ...newNotifs];
      });
    }
  }, [projects]);

  const handleSearch = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && search.trim()) {
      router.navigate({ to: "/tasks" });
      setSearch("");
    }
  };

  const userInitials = user?.full_name
    ? user.full_name.split(" ").map(n => n[0]).join("").toUpperCase()
    : "??";

  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
        <div className="h-16 flex items-center gap-2 px-5 border-b border-sidebar-border">
          <div className="h-8 w-8 rounded-lg flex items-center justify-center bg-primary text-primary-foreground shadow-sm">
            <Shield className="h-4 w-4" />
          </div>
          <span className="font-semibold tracking-tight">Team Nexus</span>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          <p className="px-3 py-2 text-xs uppercase tracking-wider text-muted-foreground/60 font-semibold">Workspace</p>
          {nav.map((item) => {
            const active = pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-200 ${
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm font-medium"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                }`}
              >
                <item.icon className={`h-4 w-4 ${active ? "text-primary" : ""}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t border-sidebar-border">
          <div className="bg-sidebar-accent/40 rounded-xl p-3 flex items-center gap-3 border border-sidebar-border/50">
            <Avatar className="h-9 w-9 border-2 border-background">
              <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">{userInitials}</AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate text-foreground">{user?.full_name || "User"}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email || ""}</p>
            </div>
            <Button size="icon" variant="ghost" className="h-8 w-8 hover:text-destructive hover:bg-destructive/10" onClick={logout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 border-b border-border flex items-center gap-4 px-6 sticky top-0 z-10 bg-background/70 backdrop-blur-xl">
          <div className="flex-1 max-w-md relative">
            <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input 
              placeholder="Search tasks, projects, people…" 
              className="pl-9 bg-card/60 border-border" 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleSearch}
            />
          </div>
          <div className="flex items-center gap-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="h-4 w-4" />
                  {notifications.length > 0 && (
                    <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary border-2 border-background" />
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-80 p-0 rounded-2xl overflow-hidden shadow-2xl border-border" align="end">
                <div className="p-4 border-b border-border bg-muted/30 flex items-center justify-between">
                  <h3 className="font-semibold text-sm">Notifications</h3>
                  <span className="text-[10px] font-bold bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">{notifications.length}</span>
                </div>
                <div className="divide-y divide-border max-h-[400px] overflow-y-auto custom-scrollbar">
                  {notifications.length > 0 ? (
                    notifications.map((n) => (
                      <div key={n.id} className="p-4 hover:bg-muted/30 transition-colors cursor-pointer group">
                        <div className="flex items-start justify-between gap-2">
                          <p className={`text-xs font-medium ${n.type === 'deadline' ? 'text-destructive' : ''}`}>{n.title}</p>
                          <span className={`h-1.5 w-1.5 rounded-full shrink-0 mt-1 ${n.type === 'deadline' ? 'bg-destructive' : 'bg-primary'}`} />
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-1 leading-relaxed">{n.description}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-10 text-center">
                      <p className="text-xs text-muted-foreground">All caught up! 🎉</p>
                    </div>
                  )}
                </div>
                {notifications.length > 0 && (
                  <div className="p-3 text-center border-t border-border bg-muted/10">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-[10px] h-auto p-2 w-full hover:bg-primary/5 hover:text-primary transition-all font-bold uppercase tracking-wider"
                      onClick={() => setNotifications([])}
                    >
                      Mark all as read
                    </Button>
                  </div>
                )}
              </PopoverContent>
            </Popover>
            
            <Button variant="ghost" size="icon" asChild>
              <Link to="/settings"><Settings className="h-4 w-4" /></Link>
            </Button>
            
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary/20 text-primary text-xs">{userInitials}</AvatarFallback>
            </Avatar>
          </div>
        </header>
        <main className="flex-1 p-6 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
