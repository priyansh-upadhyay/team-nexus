import { priorityColor, type Priority } from "@/lib/mock";

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span className={`inline-flex items-center text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-md border ${priorityColor(priority)}`}>
      {priority}
    </span>
  );
}
