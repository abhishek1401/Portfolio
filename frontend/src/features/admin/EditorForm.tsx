import type { Dashboard, DashboardLink, Project, Stat, TimelineItem } from "../../types/dashboard";
import { LabeledInput, LabeledTextarea, RemoveButton } from "../../components/FormFields";
import { CollectionEditor } from "./CollectionEditor";

interface EditorFormProps {
  draft: Dashboard;
  setDraft: (dashboard: Dashboard) => void;
  uploadingImage: boolean;
  onImageUpload: (file: File) => void;
}

const blankStat: Stat = { label: "", value: "", detail: "" };
const blankProject: Project = { name: "", description: "", status: "", link: "" };
const blankTimelineItem: TimelineItem = { date: "", title: "", description: "" };
const blankLink: DashboardLink = { label: "", url: "" };

export function EditorForm({ draft, setDraft, uploadingImage, onImageUpload }: EditorFormProps) {
  function updateUser(key: keyof Dashboard["user"], value: string) {
    setDraft({ ...draft, user: { ...draft.user, [key]: value } });
  }

  function updateSkill(index: number, value: string) {
    setDraft({
      ...draft,
      skills: draft.skills.map((skill, itemIndex) => (itemIndex === index ? value : skill)),
    });
  }

  return (
    <form className="editor-form" onSubmit={(event) => event.preventDefault()}>
      <section className="form-section">
        <h2>Profile</h2>
        <LabeledInput label="Name" value={draft.user.name} onChange={(value) => updateUser("name", value)} />
        <LabeledInput label="Title" value={draft.user.title} onChange={(value) => updateUser("title", value)} />
        <LabeledInput label="Location" value={draft.user.location} onChange={(value) => updateUser("location", value)} />
        <LabeledInput label="Email" value={draft.user.email} onChange={(value) => updateUser("email", value)} />
        <LabeledInput label="Phone" value={draft.user.phone} onChange={(value) => updateUser("phone", value)} />
        <LabeledInput label="Availability" value={draft.user.availability} onChange={(value) => updateUser("availability", value)} />
        <LabeledInput label="Focus" value={draft.user.focus} onChange={(value) => updateUser("focus", value)} />
        <LabeledInput label="Avatar URL" value={draft.user.avatarUrl} onChange={(value) => updateUser("avatarUrl", value)} />
        <label className="field">
          <span>Upload Profile Image</span>
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            disabled={uploadingImage}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                onImageUpload(file);
              }
              event.target.value = "";
            }}
          />
        </label>
        <LabeledInput label="Theme Color" type="color" value={draft.user.themeColor} onChange={(value) => updateUser("themeColor", value)} />
        <LabeledTextarea label="Bio" value={draft.user.bio} onChange={(value) => updateUser("bio", value)} />
      </section>

      <CollectionEditor
        title="Snapshot"
        items={draft.stats}
        blankItem={blankStat}
        fields={["label", "value", "detail"]}
        multiline={["detail"]}
        onChange={(stats) => setDraft({ ...draft, stats })}
      />

      <section className="form-section">
        <div className="section-heading">
          <h2>Skills</h2>
          <button type="button" className="secondary" onClick={() => setDraft({ ...draft, skills: [...draft.skills, ""] })}>
            Add
          </button>
        </div>
        {draft.skills.map((skill, index) => (
          <div className="inline-row" key={`skill-${index}`}>
            <LabeledInput label="Skill" value={skill} onChange={(value) => updateSkill(index, value)} />
            <RemoveButton onClick={() => setDraft({ ...draft, skills: draft.skills.filter((_, itemIndex) => itemIndex !== index) })} />
          </div>
        ))}
      </section>

      <CollectionEditor
        title="Projects"
        items={draft.projects}
        blankItem={blankProject}
        fields={["name", "description", "status", "link"]}
        multiline={["description"]}
        onChange={(projects) => setDraft({ ...draft, projects })}
      />

      <CollectionEditor
        title="Timeline"
        items={draft.timeline}
        blankItem={blankTimelineItem}
        fields={["date", "title", "description"]}
        multiline={["description"]}
        onChange={(timeline) => setDraft({ ...draft, timeline })}
      />

      <CollectionEditor
        title="Links"
        items={draft.links}
        blankItem={blankLink}
        fields={["label", "url"]}
        onChange={(links) => setDraft({ ...draft, links })}
      />
    </form>
  );
}
