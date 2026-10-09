import {
  CheckCircleOutline,
  ErrorOutline,
  HourglassTop,
  PendingOutlined,
  Sync,
} from "@mui/icons-material";
import { Chip, type ChipProps } from "@mui/material";

import type { WorkItemStatus } from "../types/workItems";

const statusPresentation: Record<
  WorkItemStatus,
  {
    label: string;
    color: ChipProps["color"];
    icon: React.ReactElement;
  }
> = {
  submitted: {
    label: "Submitted",
    color: "default",
    icon: <PendingOutlined />,
  },
  queued: { label: "Queued", color: "info", icon: <HourglassTop /> },
  processing: { label: "Processing", color: "warning", icon: <Sync /> },
  completed: {
    label: "Completed",
    color: "success",
    icon: <CheckCircleOutline />,
  },
  failed: { label: "Failed", color: "error", icon: <ErrorOutline /> },
};

export function StatusChip({ status }: { status: WorkItemStatus }) {
  const presentation = statusPresentation[status];
  return (
    <Chip
      color={presentation.color}
      icon={presentation.icon}
      label={presentation.label}
      size="small"
      variant={status === "submitted" ? "outlined" : "filled"}
    />
  );
}
