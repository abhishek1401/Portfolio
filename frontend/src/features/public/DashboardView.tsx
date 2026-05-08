import type { CSSProperties, ReactNode } from "react";

import type { Dashboard } from "../../types/dashboard";
import { emptyDashboard } from "../../types/dashboard";
import { safeUrl } from "../../utils/url";

interface DashboardViewProps {
  dashboard: Dashboard;
}

export function DashboardView({ dashboard }: DashboardViewProps) {
  const user = dashboard.user || emptyDashboard.user;
  const style = { "--theme-color": user.themeColor || "#176b87" } as CSSProperties;
  const avatarUrl = safeUrl(user.avatarUrl) || "/assets/default-avatar.svg";

  return (
    <main className="public-layout" style={style}>
      <section className="profile-band">
        <div className="profile-grid">
          <div className="profile-main">
            <img className="avatar" src={avatarUrl} alt={user.name || "Profile avatar"} />
            <div>
              <p className="availability">{user.availability || "Available"}</p>
              <h1>{user.name}</h1>
              <p className="title">{user.title}</p>
              <p className="focus">{user.focus}</p>
            </div>
          </div>
          <div className="contact-panel">
            <p>{user.location}</p>
            <a href={`mailto:${user.email}`}>{user.email}</a>
            <a href={`tel:${user.phone}`}>{user.phone}</a>
          </div>
        </div>
      </section>

      <section className="content-grid">
        <div className="main-column">
          <Section title="About">
            <p className="body-copy">{user.bio}</p>
          </Section>

          <Section title="Projects">
            <div className="project-list">
              {dashboard.projects.map((project, index) => (
                <article className="project-card" key={`${project.name}-${index}`}>
                  <div className="project-heading">
                    <h3>{project.name}</h3>
                    <span className="status-pill">{project.status}</span>
                  </div>
                  <p>{project.description}</p>
                  {project.link ? (
                    <a href={safeUrl(project.link)} target="_blank" rel="noreferrer">
                      Open
                    </a>
                  ) : null}
                </article>
              ))}
            </div>
          </Section>

          <Section title="Timeline">
            <div className="timeline">
              {dashboard.timeline.map((item, index) => (
                <article className="timeline-item" key={`${item.title}-${index}`}>
                  <span>{item.date}</span>
                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                  </div>
                </article>
              ))}
            </div>
          </Section>
        </div>

        <aside className="side-column">
          <Section title="Snapshot">
            <div className="stat-grid">
              {dashboard.stats.map((stat, index) => (
                <article className="stat-card" key={`${stat.label}-${index}`}>
                  <strong>{stat.value}</strong>
                  <span>{stat.label}</span>
                  <p>{stat.detail}</p>
                </article>
              ))}
            </div>
          </Section>

          <Section title="Skills">
            <div className="skill-list">
              {dashboard.skills.map((skill) => (
                <span key={skill}>{skill}</span>
              ))}
            </div>
          </Section>

          <Section title="Links">
            <div className="link-list">
              {dashboard.links.map((link, index) => (
                <a key={`${link.label}-${index}`} href={safeUrl(link.url)} target="_blank" rel="noreferrer">
                  {link.label}
                </a>
              ))}
            </div>
          </Section>
        </aside>
      </section>
    </main>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="section-block">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
