interface StatusMessageProps {
  message: string;
  tone?: "success" | "error";
}

export function StatusMessage({ message, tone = undefined }: StatusMessageProps) {
  return <div className={`status-message ${tone || ""}`}>{message}</div>;
}
