import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AppContent from "./pages/AppContent";
import DiplochainDashboard from "./pages/DiplochainDashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/audit-dashboard" element={<AppContent />} />
        <Route path="/blockchain" element={<DiplochainDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;