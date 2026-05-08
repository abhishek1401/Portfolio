export function safeUrl(url: string): string {
  if (!url) {
    return "";
  }
  return url.startsWith("http://") || url.startsWith("https://") || url.startsWith("/") ? url : "";
}
