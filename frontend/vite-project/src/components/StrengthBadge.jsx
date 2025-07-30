// src/components/StrengthBadge.jsx
const StrengthBadge = ({ strength }) => {
  const colorMap = {
    Strong: "bg-green-100 text-green-700",
    Moderate: "bg-yellow-100 text-yellow-700",
    Weak: "bg-red-100 text-red-700",
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${colorMap[strength]}`}>
      {strength || "Unknown"}
    </span>
  );
};

export default StrengthBadge;
