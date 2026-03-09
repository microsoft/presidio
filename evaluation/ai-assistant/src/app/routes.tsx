import { createBrowserRouter, Navigate } from "react-router";
import { Setup } from "./pages/Setup";
import { Anonymization } from "./pages/Anonymization";
import { HumanReview } from "./pages/HumanReview";
import { Evaluation } from "./pages/Evaluation";
import { Decision } from "./pages/Decision";
import { Layout } from "./components/Layout";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Setup },
      { path: "anonymization", Component: Anonymization },
      { path: "human-review", Component: HumanReview },
      { path: "evaluation", Component: Evaluation },
      { path: "decision", Component: Decision },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);
