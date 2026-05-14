import { createFileRoute, Link, Navigate } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: () => <Navigate to="/dashboard" />,
});

// Unused but keeps Link import valid if needed later
void Link;
