export interface DashboardUser {
  name: string;
  title: string;
  location: string;
  email: string;
  phone: string;
  availability: string;
  focus: string;
  bio: string;
  avatarUrl: string;
  themeColor: string;
}

export interface Stat {
  label: string;
  value: string;
  detail: string;
}

export interface Project {
  name: string;
  description: string;
  status: string;
  link: string;
}

export interface TimelineItem {
  date: string;
  title: string;
  description: string;
}

export interface DashboardLink {
  label: string;
  url: string;
}

export interface Dashboard {
  user: DashboardUser;
  stats: Stat[];
  skills: string[];
  projects: Project[];
  timeline: TimelineItem[];
  links: DashboardLink[];
}

export interface ProfileSummary {
  slug: string;
  name: string;
  title: string;
  avatarUrl: string;
  publicUrl: string;
  updatedAt: number;
}

export interface ProfilesResponse {
  defaultSlug: string;
  profiles: ProfileSummary[];
}

export interface ProfileResponse {
  profile: ProfileSummary;
  dashboard: Dashboard;
}

export interface CreateProfilePayload {
  name: string;
  title: string;
}

export interface ImageUploadResponse {
  avatarUrl: string;
}

export interface AdminSession {
  token: string;
  username?: string;
  expiresAt?: number;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export type EditableItem = Stat | Project | TimelineItem | DashboardLink;

export const emptyDashboard: Dashboard = {
  user: {
    name: "",
    title: "",
    location: "",
    email: "",
    phone: "",
    availability: "",
    focus: "",
    bio: "",
    avatarUrl: "/assets/default-avatar.svg",
    themeColor: "#176b87",
  },
  stats: [],
  skills: [],
  projects: [],
  timeline: [],
  links: [],
};

export function cloneDashboard(dashboard: Dashboard): Dashboard {
  return JSON.parse(JSON.stringify(dashboard)) as Dashboard;
}
