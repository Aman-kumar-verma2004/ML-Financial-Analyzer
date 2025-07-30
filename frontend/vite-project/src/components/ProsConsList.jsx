// src/components/ProsConsList.jsx
const ProsConsList = ({ title, items, isPros }) => {
  return (
    <div className="bg-white shadow-md rounded-lg p-4">
      <h3 className={`text-lg font-semibold mb-2 ${isPros ? "text-green-600" : "text-red-600"}`}>
        {isPros ? "✅ Pros" : "❌ Cons"}
      </h3>

      {items && items.length > 0 ? (
        <ul className="list-disc list-inside space-y-1">
          {items.map((item, index) => (
            <li key={index} className="text-gray-700">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500 italic">No {isPros ? "pros" : "cons"} available.</p>
      )}
    </div>
  );
};

export default ProsConsList;
