// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AllCompanies from "./pages/AllCompanies";
import CompanyDetails from "./pages/CompanyDetails";
import Navbar from "./components/Navbar";

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/all" element={<AllCompanies />} />
        <Route path="/company/:id" element={<CompanyDetails />} />
      </Routes>
    </Router>
  );
}

export default App;
