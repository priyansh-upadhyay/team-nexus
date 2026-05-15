export type Priority = "Low" | "Medium" | "High" | "Urgent" | "low" | "medium" | "high" | "urgent";
export type Status = "Todo" | "In Progress" | "Review" | "Done";

export interface Task {
  id: string;
  title: string;
  priority: Priority;
  assignee: { name: string; initials: string };
  due: string;
  status: Status;
  project?: string;
  tags?: string[];
  description?: string;
}

export const tasks: Task[] = [
  { id: "NX-101", title: "Design onboarding flow", description: "Map the first-run experience and finalize empty states.", priority: "High", assignee: { name: "Alex Morgan", initials: "AM" }, due: "May 14", status: "Todo", project: "Aurora", tags: ["design"] },
  { id: "NX-102", title: "Set up CI pipeline", description: "Configure GitHub Actions for lint, tests, and preview deploys.", priority: "Medium", assignee: { name: "Priya Shah", initials: "PS" }, due: "May 15", status: "Todo", project: "Platform" },
  { id: "NX-103", title: "Refactor billing module", description: "Split invoices, subscriptions, and tax into separate services.", priority: "Urgent", assignee: { name: "Jonas Kim", initials: "JK" }, due: "May 12", status: "In Progress", project: "Billing" },
  { id: "NX-104", title: "Implement theme tokens", description: "Centralize colors, spacing, and radii into design tokens.", priority: "Low", assignee: { name: "Mia Chen", initials: "MC" }, due: "May 20", status: "In Progress", project: "Aurora" },
  { id: "NX-105", title: "User research interviews", description: "Run six sessions with mid-market admins this sprint.", priority: "Medium", assignee: { name: "Sara Lee", initials: "SL" }, due: "May 18", status: "Review", project: "Insights" },
  { id: "NX-106", title: "API rate-limit policy", description: "Draft per-tenant limits and document the 429 contract.", priority: "High", assignee: { name: "Diego Ruiz", initials: "DR" }, due: "May 13", status: "Review", project: "Platform" },
  { id: "NX-107", title: "Launch landing v2", description: "Ship redesigned marketing site with new positioning.", priority: "High", assignee: { name: "Alex Morgan", initials: "AM" }, due: "May 09", status: "Done", project: "Marketing" },
  { id: "NX-108", title: "Migrate to Postgres 16", description: "Cutover with zero downtime using logical replication.", priority: "Medium", assignee: { name: "Jonas Kim", initials: "JK" }, due: "May 06", status: "Done", project: "Platform" },
  { id: "NX-109", title: "Mobile nav polish", description: "Refine tap targets and animation timing on small screens.", priority: "Low", assignee: { name: "Mia Chen", initials: "MC" }, due: "May 22", status: "Todo", project: "Aurora" },
  { id: "NX-110", title: "Audit log dashboard", description: "Surface security events with filters and CSV export.", priority: "Medium", assignee: { name: "Priya Shah", initials: "PS" }, due: "May 24", status: "In Progress", project: "Security" },
];

export const projects = [
  { name: "Aurora", desc: "Next-gen product surface", progress: 62, members: 8, due: "Jun 12", color: "from-violet-500 to-fuchsia-500" },
  { name: "Platform", desc: "Core infra & APIs", progress: 84, members: 5, due: "May 30", color: "from-sky-500 to-cyan-500" },
  { name: "Billing", desc: "Subscriptions & invoices", progress: 41, members: 4, due: "Jul 02", color: "from-amber-500 to-rose-500" },
  { name: "Insights", desc: "Analytics & reporting", progress: 28, members: 6, due: "Jul 18", color: "from-emerald-500 to-teal-500" },
  { name: "Marketing", desc: "Web & campaigns", progress: 95, members: 3, due: "May 10", color: "from-pink-500 to-rose-500" },
  { name: "Security", desc: "Compliance & audits", progress: 55, members: 4, due: "Aug 01", color: "from-indigo-500 to-blue-500" },
];

export const teams = [
  { name: "Product Design", lead: "Alex Morgan", members: 6, tag: "Design" },
  { name: "Platform Engineering", lead: "Jonas Kim", members: 9, tag: "Engineering" },
  { name: "Growth", lead: "Sara Lee", members: 4, tag: "Marketing" },
  { name: "Customer Success", lead: "Priya Shah", members: 5, tag: "Operations" },
  { name: "Data & ML", lead: "Mia Chen", members: 7, tag: "Engineering" },
  { name: "Security", lead: "Diego Ruiz", members: 3, tag: "Engineering" },
];

export function priorityColor(p: Priority): string {
  const normalized = p?.toLowerCase();
  switch (normalized) {
    case "urgent": return "bg-destructive/15 text-destructive border-destructive/30";
    case "high": return "bg-warning/15 text-warning border-warning/30";
    case "medium": return "bg-info/15 text-info border-info/30";
    case "low": return "bg-muted text-muted-foreground border-border";
    default: return "bg-muted text-muted-foreground border-border";
  }
}
