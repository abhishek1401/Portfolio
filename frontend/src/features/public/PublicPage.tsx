import { useEffect, useMemo, useState } from "react";

import { api } from "../../api/client";
import { StatusMessage } from "../../components/StatusMessage";
import type { Dashboard, ProfileResponse } from "../../types/dashboard";
import { DashboardView } from "./DashboardView";

export function PublicPage() {
  const slug = useMemo(() => profileSlugFromPath(window.location.pathname), []);

  if (slug) {
    return <PublicProfile slug={slug} />;
  }

  return <DefaultPublicProfile />;
}

function DefaultPublicProfile() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Dashboard>("/api/public")
      .then(setDashboard)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return <StatusMessage tone="error" message={error} />;
  }

  if (!dashboard) {
    return <StatusMessage message="Loading profile..." />;
  }

  return <DashboardView dashboard={dashboard} />;
}

function PublicProfile({ slug }: { slug: string }) {
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api<ProfileResponse>(`/api/public/profiles/${encodeURIComponent(slug)}`)
      .then(setProfile)
      .catch((err: Error) => setError(err.message));
  }, [slug]);

  if (error) {
    return <StatusMessage tone="error" message={error} />;
  }

  if (!profile) {
    return <StatusMessage message="Loading profile..." />;
  }

  return <DashboardView dashboard={profile.dashboard} />;
}

function profileSlugFromPath(pathname: string): string {
  const prefix = "/profile/";
  if (!pathname.startsWith(prefix)) {
    return "";
  }
  return decodeURIComponent(pathname.slice(prefix.length).split("/")[0] || "");
}
