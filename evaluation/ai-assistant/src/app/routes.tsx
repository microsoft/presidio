import { createBrowserRouter, Navigate } from "react-router";
import { Setup } from "./pages/Setup";
import { Sampling } from "./pages/Sampling";
import { Anonymization } from "./pages/Anonymization";
import { HumanReview } from "./pages/HumanReview";
import { Evaluation } from "./pages/Evaluation";
import { Dashboard } from "./pages/Dashboard";
import { Decision } from "./pages/Decision";
import { Layout } from "./components/Layout";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Setup },
      { path: "sampling", Component: Sampling },
      { path: "anonymization", Component: Anonymization },
      { path: "human-review", Component: HumanReview },
      { path: "evaluation", Component: Evaluation },
      { path: "dashboard", Component: Dashboard },
      { path: "decision", Component: Decision },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);
