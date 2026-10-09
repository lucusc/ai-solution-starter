const dateFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "short",
});

export function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unknown" : dateFormatter.format(date);
}
