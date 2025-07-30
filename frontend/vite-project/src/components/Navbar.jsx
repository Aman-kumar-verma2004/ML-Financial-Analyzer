// src/components/Navbar.jsx
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-white shadow px-6 py-3 flex justify-between items-center">
      <Link to="/" className="text-xl font-bold text-indigo-700">
        ML Financial Analyzer
      </Link>
      <div className="space-x-4">
        <Link to="/" className="text-sm text-gray-700 hover:text-indigo-600">
          Home
        </Link>
        <Link to="/all" className="text-sm text-gray-700 hover:text-indigo-600">
          All Companies
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
