export function showToast(message: string) {
  const event = new CustomEvent("toast", { detail: { message } });
  window.dispatchEvent(event);
}
