import type { HTMLInputTypeAttribute } from "react";

interface InputProps {
  label: string;
  value: string;
  type?: HTMLInputTypeAttribute;
  onChange: (value: string) => void;
}

interface TextareaProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

export function LabeledInput({ label, value, type = "text", onChange }: InputProps) {
  return (
    <label className="field">
      <span>{label}</span>
      <input type={type} value={value || ""} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

export function LabeledTextarea({ label, value, onChange }: TextareaProps) {
  return (
    <label className="field">
      <span>{label}</span>
      <textarea value={value || ""} rows={4} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

export function RemoveButton({ onClick }: { onClick: () => void }) {
  return (
    <button type="button" className="danger" onClick={onClick}>
      Remove
    </button>
  );
}
