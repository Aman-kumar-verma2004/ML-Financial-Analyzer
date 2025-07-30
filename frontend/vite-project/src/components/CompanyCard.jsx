import { Link } from "react-router-dom";
import StrengthBadge from "./StrengthBadge";

const CompanyCard = ({ company }) => {
  return (
    <div className="bg-white shadow rounded-xl p-4 hover:shadow-md transition duration-200">
      <div className="flex items-center gap-4">
        <img
          src={company.company_logo || "https://bluemutualfund.in/app1/public/dummy-logo.png"}
          alt="Logo"
          className="h-12 w-12 object-contain"
        />
        <div>
          <h2 className="text-lg font-semibold">{company.company}</h2>
          <p className="text-sm text-gray-500">{company.id || "N/A"}</p>
        </div>
      </div>

      <div className="mt-4">
        <StrengthBadge strength={company.strngth} />
      </div>

      {/* ✅ IMPORTANT: company.id ke jagah company.company bhej rahe hain */}
      <Link
        to={`/company/${company.company}`}
        className="block mt-4 text-indigo-600 hover:underline text-sm"
      >
        View Details →
      </Link>
    </div>
  );
};

export default CompanyCard;
