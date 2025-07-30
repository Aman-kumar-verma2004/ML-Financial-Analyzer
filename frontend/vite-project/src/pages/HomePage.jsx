// src/pages/HomePage.jsx
import { Link } from "react-router-dom";

const HomePage = () => {
  return (
    <div className="text-center py-20 px-6">
      <h1 className="text-4xl font-bold mb-4">ML-Based Financial Insights</h1>
      <p className="text-gray-600 text-lg mb-6 max-w-xl mx-auto">
        We analyze financial statements using machine learning to determine the strength of NIFTY100 companies and display key pros & cons.
      </p>
      <Link to="/all" className="bg-indigo-600 text-white px-6 py-2 rounded-full hover:bg-indigo-700 transition">
        View All Companies
      </Link>
    </div>
  );
};

export default HomePage;
