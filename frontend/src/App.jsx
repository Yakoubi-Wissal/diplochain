import React from "react";
import Dashboard from "./DiploChain_Dashboard_v3";
import VerificationPage from "./pages/VerificationPage";

// simple routing without a router: if path starts with /verify show public page
export default function App() {
  const path = window.location.pathname || "/";
  if (path.startsWith("/verify")) {
    return <VerificationPage />;
  }
  return <Dashboard />;
}
