import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import Loader from "../components/Loader";
import ProsConsList from "../components/ProsConsList";

const CompanyDetails = () => {
  const { id } = useParams();
  const [company, setCompany] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:5000/api/companies/${id}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        return res.json();
      })
      .then((data) => {
        setCompany(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
        console.error("❌ Failed to fetch company details:", err);
      });
  }, [id]);

  if (loading) return <Loader />;
  if (error) return <div className="p-6 text-center text-red-500">❌ Error: Could not load company details.</div>;
  if (!company) return <div className="p-6 text-center">No company data found.</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-6">
        <img
          src={company.company_logo || "https://bluemutualfund.in/app1/public/dummy-logo.png"}
          alt="Company Logo"
          className="h-16 w-16 object-contain"
        />
        <div>
          <h2 className="text-2xl font-bold">{company.company_name}</h2>
          <p className="text-sm text-gray-600">{company.id}</p>
        </div>
      </div>

      <div className="mt-6 space-y-4">
        <ProsConsList title="✅ Pros" items={company.pros || []} isPros={true} />
        <ProsConsList title="❌ Cons" items={company.cons || []} isPros={false} />
      </div>
    </div>
  );
};

export default CompanyDetails;
