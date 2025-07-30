// src/pages/AllCompanies.jsx
import { useEffect, useState } from "react";
import CompanyCard from "../components/CompanyCard";
import Loader from "../components/Loader";


const AllCompanies = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5000/api/companies")
      .then((res) => res.json())
      .then((data) => {
        console.log('Fetched data:', data);
        setCompanies(data);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6 text-center">Analyzed Companies</h2>
      {loading ? (
        <Loader />
      ) : (
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {companies.map((c) => (
            <CompanyCard key={c.id} company={c} />
          ))}
        </div>
      )}
    </div>
  );
};

export default AllCompanies;
