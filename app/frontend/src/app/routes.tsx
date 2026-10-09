import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "../components/AppShell";
import { DashboardPage } from "../pages/DashboardPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { WorkItemDetailPage } from "../pages/WorkItemDetailPage";

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/work-items/:id", element: <WorkItemDetailPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
