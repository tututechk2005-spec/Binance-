import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import App from "./App";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#1e2026",
            color: "#eaecef",
            border: "1px solid #2b2f36",
            borderRadius: "8px",
            fontSize: "14px",
          },
          success: { iconTheme: { primary: "#0ecb81", secondary: "#1e2026" } },
          error: { iconTheme: { primary: "#f6465d", secondary: "#1e2026" } },
        }}
      />
    </QueryClientProvider>
  </React.StrictMode>
);
