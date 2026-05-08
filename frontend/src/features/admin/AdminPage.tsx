import { FormEvent, useEffect, useState } from "react";

import { api } from "../../api/client";
import { LabeledInput } from "../../components/FormFields";
import { StatusMessage } from "../../components/StatusMessage";
import type {
  AdminSession,
  CreateProfilePayload,
  Dashboard,
  ImageUploadResponse,
  LoginPayload,
  ProfileResponse,
  ProfileSummary,
  ProfilesResponse,
} from "../../types/dashboard";
import { cloneDashboard } from "../../types/dashboard";
import { safeUrl } from "../../utils/url";
import { DashboardView } from "../public/DashboardView";
import { EditorForm } from "./EditorForm";
import { LoginPanel } from "./LoginPanel";

export function AdminPage() {
  const [session, setSession] = useState<AdminSession | null>(() => {
    const token = window.localStorage.getItem("adminToken");
    return token ? { token } : null;
  });
  const [profiles, setProfiles] = useState<ProfileSummary[]>([]);
  const [activeSlug, setActiveSlug] = useState("");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [draft, setDraft] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (!session) {
      return;
    }
    loadProfiles();
  }, [session]);

  useEffect(() => {
    if (!session || !activeSlug) {
      return;
    }
    loadProfile(activeSlug);
  }, [session, activeSlug]);

  async function loadProfiles(preferredSlug = "") {
    try {
      const data = await api<ProfilesResponse>("/api/admin/profiles");
      setProfiles(data.profiles);
      const nextSlug = preferredSlug || activeSlug || data.defaultSlug || data.profiles[0]?.slug || "";
      setActiveSlug(nextSlug);
      setError("");
    } catch (err) {
      window.localStorage.removeItem("adminToken");
      setSession(null);
      setError((err as Error).message);
    }
  }

  async function loadProfile(slug: string) {
    try {
      const data = await api<ProfileResponse>(`/api/admin/profiles/${encodeURIComponent(slug)}`);
      setDashboard(data.dashboard);
      setDraft(cloneDashboard(data.dashboard));
      setError("");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleLogin(credentials: LoginPayload) {
    setError("");
    try {
      const data = await api<AdminSession>("/api/admin/login", {
        method: "POST",
        body: JSON.stringify(credentials),
      });
      window.localStorage.setItem("adminToken", data.token);
      setSession(data);
      setNotice("Signed in.");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleCreateProfile(payload: CreateProfilePayload) {
    setError("");
    setNotice("");
    try {
      const data = await api<ProfileResponse>("/api/admin/profiles", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      await loadProfiles(data.profile.slug);
      setDashboard(data.dashboard);
      setDraft(cloneDashboard(data.dashboard));
      setNotice(`Created ${data.profile.name}.`);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleSave() {
    if (!draft || !activeSlug) {
      return;
    }

    setSaving(true);
    setError("");
    setNotice("");
    try {
      const data = await api<ProfileResponse>(`/api/admin/profiles/${encodeURIComponent(activeSlug)}`, {
        method: "PUT",
        body: JSON.stringify(draft),
      });
      setDashboard(data.dashboard);
      setDraft(cloneDashboard(data.dashboard));
      await loadProfiles(activeSlug);
      setNotice(`Saved ${data.profile.name} to cfg/profiles/${data.profile.slug}.json.`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!activeSlug) {
      return;
    }
    const activeProfile = profiles.find((profile) => profile.slug === activeSlug);
    const confirmed = window.confirm(`Delete ${activeProfile?.name || activeSlug}? This removes its profile cfg file.`);
    if (!confirmed) {
      return;
    }

    setError("");
    setNotice("");
    try {
      const data = await api<ProfilesResponse>(`/api/admin/profiles/${encodeURIComponent(activeSlug)}`, {
        method: "DELETE",
      });
      setProfiles(data.profiles);
      setActiveSlug(data.defaultSlug || data.profiles[0]?.slug || "");
      setNotice("Profile deleted.");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function handleImageUpload(file: File) {
    if (!draft || !activeSlug) {
      return;
    }
    const body = new FormData();
    body.append("image", file);

    setUploading(true);
    setError("");
    setNotice("");
    try {
      const data = await api<ImageUploadResponse>(`/api/admin/profiles/${encodeURIComponent(activeSlug)}/image`, {
        method: "POST",
        body,
      });
      setDraft({ ...draft, user: { ...draft.user, avatarUrl: data.avatarUrl } });
      setNotice("Image uploaded. Save the profile to publish it.");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  }

  function handleLogout() {
    api<{ status: string }>("/api/admin/logout", { method: "POST", body: "{}" }).finally(() => {
      window.localStorage.removeItem("adminToken");
      setSession(null);
      setProfiles([]);
      setActiveSlug("");
      setDashboard(null);
      setDraft(null);
    });
  }

  if (!session) {
    return (
      <main className="admin-layout">
        <LoginPanel onLogin={handleLogin} error={error} />
      </main>
    );
  }

  return (
    <main className="admin-layout">
      <div className="admin-toolbar">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>Manage Profiles</h1>
        </div>
        <div className="toolbar-actions">
          <button type="button" className="secondary" onClick={handleLogout}>
            Sign out
          </button>
          <button type="button" onClick={handleSave} disabled={saving || !draft}>
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      {notice ? <StatusMessage tone="success" message={notice} /> : null}
      {error ? <StatusMessage tone="error" message={error} /> : null}

      <div className="admin-workspace">
        <aside className="profile-manager">
          <CreateProfilePanel onCreate={handleCreateProfile} />
          <ProfileList profiles={profiles} activeSlug={activeSlug} onSelect={setActiveSlug} />
        </aside>

        {draft ? (
          <div className="editor-grid">
            <div>
              <div className="profile-actions">
                <a href={`/profile/${activeSlug}`} target="_blank" rel="noreferrer">
                  Open public URL
                </a>
                <button type="button" className="secondary" onClick={() => dashboard && setDraft(cloneDashboard(dashboard))}>
                  Reset
                </button>
                <button type="button" className="danger" onClick={handleDelete}>
                  Delete
                </button>
              </div>
              <EditorForm draft={draft} setDraft={setDraft} uploadingImage={uploading} onImageUpload={handleImageUpload} />
            </div>
            <div className="preview-shell">
              <p className="eyebrow">Public Preview</p>
              <DashboardView dashboard={draft} />
            </div>
          </div>
        ) : (
          <StatusMessage message="Select or create a profile." />
        )}
      </div>
    </main>
  );
}

function CreateProfilePanel({ onCreate }: { onCreate: (payload: CreateProfilePayload) => Promise<void> }) {
  const [name, setName] = useState("");
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreating(true);
    try {
      await onCreate({ name, title });
      setName("");
      setTitle("");
    } finally {
      setCreating(false);
    }
  }

  return (
    <form className="profile-create-panel" onSubmit={submit}>
      <h2>Add Profile</h2>
      <LabeledInput label="Name" value={name} onChange={setName} />
      <LabeledInput label="Title" value={title} onChange={setTitle} />
      <button type="submit" disabled={creating}>
        {creating ? "Adding..." : "Add profile"}
      </button>
    </form>
  );
}

function ProfileList({
  profiles,
  activeSlug,
  onSelect,
}: {
  profiles: ProfileSummary[];
  activeSlug: string;
  onSelect: (slug: string) => void;
}) {
  return (
    <section className="profile-list-panel">
      <h2>Profiles</h2>
      <div className="profile-list">
        {profiles.map((profile) => (
          <button
            type="button"
            className={`profile-list-item ${profile.slug === activeSlug ? "active" : ""}`}
            key={profile.slug}
            onClick={() => onSelect(profile.slug)}
          >
            <img src={safeUrl(profile.avatarUrl) || "/assets/default-avatar.svg"} alt="" />
            <span>{profile.name}</span>
            <strong>{profile.title || profile.slug}</strong>
          </button>
        ))}
      </div>
    </section>
  );
}
