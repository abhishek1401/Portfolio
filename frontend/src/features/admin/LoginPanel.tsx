import { FormEvent, useState } from "react";

import { LabeledInput } from "../../components/FormFields";
import { StatusMessage } from "../../components/StatusMessage";
import type { LoginPayload } from "../../types/dashboard";

interface LoginPanelProps {
  error: string;
  onLogin: (credentials: LoginPayload) => Promise<void>;
}

export function LoginPanel({ error, onLogin }: LoginPanelProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    try {
      await onLogin({ username, password });
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="login-panel" onSubmit={submit}>
      <p className="eyebrow">Admin Access</p>
      <h1>Sign in</h1>
      {error ? <StatusMessage tone="error" message={error} /> : null}
      <LabeledInput label="Username" value={username} onChange={setUsername} />
      <LabeledInput label="Password" type="password" value={password} onChange={setPassword} />
      <button type="submit" disabled={busy}>
        {busy ? "Signing in..." : "Sign in"}
      </button>
    </form>
  );
}
