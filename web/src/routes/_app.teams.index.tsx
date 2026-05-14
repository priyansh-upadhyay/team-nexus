import { useState } from "react";
import { createFileRoute, Link } from '@tanstack/react-router'
import { teamsApi } from "@/lib/api/teams";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2, AlertCircle, MoreHorizontal, Search, Trash, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { CreateTeamDialog } from "@/components/teams/CreateTeamDialog";
import { EditTeamDialog } from "@/components/teams/EditTeamDialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { toast } from "sonner";

export const Route = createFileRoute("/_app/teams/")({
  head: () => ({ meta: [{ title: "Teams — Team Nexus" }] }),
  component: TeamsPage,
});

function TeamsPage() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [editingTeam, setEditingTeam] = useState<{ id: number; name: string; description: string | null } | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const { data: teams, isLoading, error } = useQuery({
    queryKey: ["teams"],
    queryFn: () => teamsApi.list(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => teamsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] });
      toast.success("Team deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete team");
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
        <p className="text-sm font-medium text-foreground">Failed to load teams</p>
      </div>
    );
  }

  const filteredTeams = teams?.filter(t => 
    t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">Teams</h1>
          <p className="text-sm text-muted-foreground mt-1">Organize people by function or product.</p>
        </div>
        <CreateTeamDialog />
      </div>

      <div className="relative max-w-sm">
        <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <Input 
          placeholder="Search teams" 
          className="pl-9 bg-card" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredTeams.length > 0 ? (
          filteredTeams.map((t) => (
            <Link key={t.id} to="/teams/$teamId" params={{ teamId: t.id.toString() }}>
              <Card className="rounded-2xl p-6 hover:shadow-md transition-all border border-border bg-card h-full group">
                <div className="flex items-start justify-between">
                  <div className="h-11 w-11 rounded-xl flex items-center justify-center text-sm font-bold bg-primary/10 text-primary border border-primary/20 shadow-sm group-hover:bg-primary group-hover:text-primary-foreground transition-all">
                    {t.name.charAt(0).toUpperCase()}
                  </div>
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
                        setEditingTeam(t);
                        setIsEditDialogOpen(true);
                      }}>
                        <Pencil className="h-4 w-4 mr-2" /> Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-destructive focus:text-destructive focus:bg-destructive/10"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          if (confirm(`Are you sure you want to delete "${t.name}"?`)) {
                            deleteMutation.mutate(t.id);
                          }
                        }}
                      >
                        <Trash className="h-4 w-4 mr-2" /> Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <h3 className="font-semibold mt-4 text-foreground text-lg group-hover:text-primary transition-colors">{t.name}</h3>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-2 leading-relaxed">{t.description || "No description provided for this team."}</p>
                <div className="flex items-center justify-between mt-6">
                  <div className="flex -space-x-2">
                    {[1, 2, 3].map((_, i) => (
                      <Avatar key={i} className="h-7 w-7 border-2 border-card shadow-sm">
                        <AvatarFallback className="text-[10px] bg-secondary text-secondary-foreground font-bold">{String.fromCharCode(65 + i)}</AvatarFallback>
                      </Avatar>
                    ))}
                  </div>
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest bg-muted px-2 py-0.5 rounded">Owner ID: {t.owner_id}</span>
                </div>
              </Card>
            </Link>
          ))
        ) : (
          <div className="col-span-full py-20 text-center border border-dashed border-border rounded-2xl bg-muted/20">
            <p className="text-muted-foreground font-medium">No teams found. Join or create a team to start collaborating.</p>
          </div>
        )}
      </div>
      {editingTeam && (
        <EditTeamDialog 
          team={editingTeam} 
          open={isEditDialogOpen} 
          onOpenChange={setIsEditDialogOpen} 
        />
      )}
    </div>
  );
}
