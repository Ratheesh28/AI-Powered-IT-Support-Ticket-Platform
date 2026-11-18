export function priorityClass(priority) {
  const level = String(priority || "Medium").toLowerCase();
  return `priority-badge priority-${level}`;
}

export function categoryClass(category) {
  const slug = String(category || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

  return `category-badge category-${slug || "unknown"}`;
}

export function formatConfidence(value) {
  if (value == null || Number.isNaN(Number(value))) {
    return "—";
  }

  return `${(Number(value) * 100).toFixed(2)}%`;
}

export function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString();
}
