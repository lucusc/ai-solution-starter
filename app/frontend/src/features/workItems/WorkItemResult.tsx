import { Box, Chip, Divider, Stack, Typography } from "@mui/material";

interface WorkItemResultProps {
  result: Record<string, unknown>;
}

const MAX_DEPTH = 4;
const MAX_ITEMS = 25;

function ResultValue({ value, depth = 0 }: { value: unknown; depth?: number }) {
  if (depth >= MAX_DEPTH) {
    return <Typography color="text.secondary">Additional detail omitted</Typography>;
  }
  if (value === null) return <Typography color="text.secondary">None</Typography>;
  if (typeof value === "string" || typeof value === "number") {
    return <Typography sx={{ overflowWrap: "anywhere" }}>{String(value)}</Typography>;
  }
  if (typeof value === "boolean") return <Typography>{value ? "Yes" : "No"}</Typography>;
  if (Array.isArray(value)) {
    return (
      <Stack component="ul" gap={0.5} pl={2.5} my={0}>
        {value.slice(0, MAX_ITEMS).map((entry, index) => (
          <Box component="li" key={index}>
            <ResultValue value={entry} depth={depth + 1} />
          </Box>
        ))}
        {value.length > MAX_ITEMS && (
          <Typography component="li" color="text.secondary">
            Additional items omitted
          </Typography>
        )}
      </Stack>
    );
  }
  if (typeof value === "object") {
    return (
      <Stack gap={1}>
        {Object.entries(value)
          .sort(([left], [right]) => left.localeCompare(right))
          .slice(0, MAX_ITEMS)
          .map(([key, entry]) => (
            <Box key={key}>
              <Typography variant="caption" color="text.secondary">
                {key}
              </Typography>
              <ResultValue value={entry} depth={depth + 1} />
            </Box>
          ))}
      </Stack>
    );
  }
  return <Typography color="text.secondary">Unavailable</Typography>;
}

export function WorkItemResult({ result }: WorkItemResultProps) {
  const summary = typeof result.summary === "string" ? result.summary : null;
  const category = typeof result.category === "string" ? result.category : null;
  const remaining = Object.fromEntries(
    Object.entries(result).filter(([key]) => !["summary", "category"].includes(key)),
  );
  return (
    <Stack gap={2}>
      <Stack direction="row" alignItems="center" gap={1}>
        <Typography variant="h6">AI result</Typography>
        {category && <Chip label={category} color="secondary" size="small" />}
      </Stack>
      {summary && <Typography>{summary}</Typography>}
      {Object.keys(remaining).length > 0 && (
        <>
          {(summary || category) && <Divider />}
          <ResultValue value={remaining} />
        </>
      )}
      {!summary && !category && Object.keys(remaining).length === 0 && (
        <Typography color="text.secondary">No result details were returned.</Typography>
      )}
    </Stack>
  );
}
