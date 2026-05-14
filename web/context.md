# Nexus Zenith Frontend - Project Context

## Project Overview
**Team Nexus** is a modern project management and team collaboration application built with React and TanStack Start. The frontend provides a comprehensive dashboard for managing teams, projects, tasks, and task boards.

## Tech Stack & Architecture

### Core Technologies
- **Framework**: React 19.2.0 with TanStack Start (SSR/SSG)
- **Routing**: TanStack Router with file-based routing
- **Styling**: Tailwind CSS 4.2.1 with shadcn/ui components
- **State Management**: TanStack Query for server state
- **Build Tool**: Vite 7.3.1
- **Deployment**: Cloudflare Workers (via Wrangler)
- **Language**: TypeScript 5.8.3

### UI Component System
- **Design System**: shadcn/ui (New York style)
- **Component Library**: Radix UI primitives
- **Icons**: Lucide React
- **Styling**: CSS Variables with Tailwind
- **Theme**: Slate base color with dark/light mode support

## Project Structure

```
nexus-zenith-frontend/
├── .lovable/                 # Lovable platform configuration
├── .tanstack/               # TanStack build artifacts
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components
│   │   │   └── AppLayout.tsx # Main app shell with sidebar/header
│   │   ├── ui/              # shadcn/ui component library (50+ components)
│   │   └── PriorityBadge.tsx # Custom priority indicator
│   ├── hooks/
│   │   └── use-mobile.tsx   # Mobile detection hook
│   ├── lib/
│   │   ├── api.ts           # API client with auth handling
│   │   ├── error-capture.ts # Error handling utilities
│   │   ├── mock.ts          # Mock data for development
│   │   └── utils.ts         # Utility functions
│   ├── routes/              # File-based routing
│   │   ├── __root.tsx       # Root layout with error boundaries
│   │   ├── _app.tsx         # App layout wrapper
│   │   ├── _app.dashboard.tsx # Dashboard page
│   │   ├── _app.kanban.tsx  # Kanban board
│   │   ├── _app.projects.tsx # Projects management
│   │   ├── _app.tasks.tsx   # Task management
│   │   ├── _app.teams.tsx   # Team management
│   │   ├── index.tsx        # Root redirect to dashboard
│   │   ├── login.tsx        # Authentication
│   │   └── register.tsx     # User registration
│   ├── router.tsx           # Router configuration
│   ├── routeTree.gen.ts     # Generated route tree
│   ├── server.ts            # SSR server entry
│   ├── start.ts             # Client entry point
│   └── styles.css           # Global styles and Tailwind
├── package.json             # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite build configuration
├── wrangler.jsonc           # Cloudflare Workers config
└── components.json          # shadcn/ui configuration
```

## Key Features & Pages

### 1. Dashboard (`/_app/dashboard`)
- **Overview**: Main landing page with project metrics and recent activity
- **Components**: Stats cards, recent tasks list, project progress charts
- **Data**: Mock data from `lib/mock.ts`

### 2. Teams Management (`/_app/teams`)
- Team listing and management interface
- Team member organization

### 3. Projects (`/_app/projects`)
- Project overview and management
- Progress tracking and team assignments

### 4. Tasks (`/_app/tasks`)
- Task management interface
- Priority-based organization with custom PriorityBadge component

### 5. Task Board (`/_app/kanban`)
- Visual task management
- Drag-and-drop functionality (implied)

### 6. Authentication
- Login/Register pages with form handling
- JWT token management via localStorage
- API integration ready

## Data Models

### Task Interface
```typescript
interface Task {
  id: string;           // Format: "NX-101"
  title: string;
  priority: "Low" | "Medium" | "High" | "Urgent";
  assignee: { name: string; initials: string };
  due: string;          // Format: "May 14"
  status: "Todo" | "In Progress" | "Review" | "Done";
  project?: string;
  tags?: string[];
  description?: string;
}
```

### Project Interface
```typescript
interface Project {
  name: string;
  desc: string;
  progress: number;     // 0-100
  members: number;
  due: string;
  color: string;        // Tailwind gradient classes
}
```

## API Integration

### API Client (`lib/api.ts`)
- **Base URL**: Configurable via `VITE_API_BASE_URL` (defaults to localhost:8000)
- **Authentication**: Bearer token with localStorage persistence
- **Error Handling**: Custom ApiError class with status codes
- **Features**: JSON/form-data support, automatic token injection

### Authentication Flow
```typescript
// Login endpoint
POST /auth/login
Body: { email: string, password: string }
Response: { access_token: string, token_type?: string }
```

## Styling & Design System

### Theme Configuration
- **Base Color**: Slate
- **CSS Variables**: Enabled for dynamic theming
- **Components**: New York style from shadcn/ui
- **Icons**: Lucide React library
- **Responsive**: Mobile-first with `md:` breakpoints

### Custom Styling
- **Glass Effect**: Used throughout for modern UI
- **Color Coding**: Priority-based color system
- **Typography**: Tailwind's font system with custom tracking
- **Animations**: CSS transitions and hover effects

## Development Workflow

### Scripts
```bash
npm run dev          # Development server
npm run build        # Production build
npm run build:dev    # Development build
npm run preview      # Preview production build
npm run lint         # ESLint checking
npm run format       # Prettier formatting
```

### Code Quality
- **ESLint**: Configured with React and TypeScript rules
- **Prettier**: Code formatting with custom config
- **TypeScript**: Strict mode enabled with path aliases

## Deployment

### Cloudflare Workers
- **Platform**: Cloudflare Workers with Node.js compatibility
- **Configuration**: `wrangler.jsonc` for deployment settings
- **SSR**: Server-side rendering support via TanStack Start
- **Build**: Vite handles bundling for Workers environment

## Environment Variables
- `VITE_API_BASE_URL`: Backend API base URL (default: http://localhost:8000)

## Mock Data
The application includes comprehensive mock data for development:
- **10 sample tasks** with various priorities and statuses
- **6 sample projects** with progress tracking
- **6 sample teams** with different specializations
- **Color-coded priority system** for visual organization

## Key Dependencies
- **UI**: @radix-ui/* components, lucide-react icons
- **Routing**: @tanstack/react-router, @tanstack/react-start
- **State**: @tanstack/react-query
- **Forms**: react-hook-form, @hookform/resolvers, zod
- **Styling**: tailwindcss, class-variance-authority, clsx
- **Charts**: recharts for data visualization
- **Utilities**: date-fns, cmdk for command palette

## Architecture Patterns
- **File-based Routing**: TanStack Router with automatic route generation
- **Component Composition**: Radix UI primitives with custom styling
- **Error Boundaries**: Comprehensive error handling at route level
- **SSR/SSG**: Server-side rendering with TanStack Start
- **Type Safety**: Full TypeScript coverage with strict configuration