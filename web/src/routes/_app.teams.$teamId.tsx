import { createFileRoute, Link } from '@tanstack/react-router'
import { teamsApi } from "@/lib/api/teams";
import { projectsApi } from "@/lib/api/projects";
import { useQuery } from "@tanstack/react-query";
import { Loader2, AlertCircle, ArrowLeft, Users, FolderKanban, Plus, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { CreateProjectDialog } from "@/components/projects/CreateProjectDialog";

export const Route = createFileRoute("/_app/teams/$teamId")({
  head: () => ({ meta: [{ title: "Team Details — Team Nexus" }] }),
  component: TeamDetailPage,
});

function TeamDetailPage() {
  const { teamId } = Route.useParams();
  const id = parseInt(teamId);

  if (isNaN(id)) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <h2 className="text-xl font-semibold">Invalid Team ID</h2>
        <Button asChild variant="outline">
          <Link to="/teams">Back to teams</Link>
        </Button>
      </div>
    );
  }

  const { data: team, isLoading: teamLoading } = useQuery({
    queryKey: ["team", id],
    queryFn: () => teamsApi.get(id),
  });

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ["projects", "team", id],
    queryFn: () => projectsApi.list(id),
  });

  if (teamLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!team) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <h2 className="text-xl font-semibold">Team not found</h2>
        <Button asChild variant="outline">
          <Link to="/teams">Back to teams</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/teams"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">{team.name}</h1>
          <p className="text-sm text-muted-foreground mt-1">{team.description || "No description provided."}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2">
            <UserPlus className="h-4 w-4" /> Invite member
          </Button>
          <CreateProjectDialog />
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
              <FolderKanban className="h-5 w-5 text-primary/80" /> Projects
            </h2>
          </div>
          
          <div className="grid sm:grid-cols-2 gap-4">
            {projectsLoading ? (
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            ) : projects && projects.length > 0 ? (
              projects.map((p) => (
                <Link key={p.id} to="/projects/$projectId" params={{ projectId: p.id.toString() }}>
                  <Card className="p-5 rounded-2xl hover:shadow-md transition-all border border-border bg-card h-full group">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="font-semibold group-hover:text-primary transition-colors truncate">{p.name}</h3>
                      <span className="text-[10px] font-bold text-muted-foreground uppercase bg-muted px-1.5 py-0.5 rounded">{p.status}</span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 mb-4">{p.description || "No description"}</p>
                    <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-primary/60 w-[30%]" />
                    </div>
                  </Card>
                </Link>
              ))
            ) : (
              <Card className="col-span-full p-12 text-center border-dashed bg-muted/10">
                <p className="text-sm text-muted-foreground">No projects found in this team.</p>
                <Button variant="link" className="mt-2">Start your first project</Button>
              </Card>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
            <Users className="h-5 w-5 text-primary/80" /> Members
          </h2>
          <Card className="p-6 rounded-2xl border border-border bg-card shadow-sm">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Avatar className="h-9 w-9 border-2 border-background">
                  <AvatarFallback className="bg-primary/10 text-primary text-xs font-bold">O</AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">Team Owner</p>
                  <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Owner</p>
                </div>
              </div>
              <div className="pt-4 border-t border-border">
                <p className="text-xs text-muted-foreground text-center">Manage team membership to see more people here.</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
