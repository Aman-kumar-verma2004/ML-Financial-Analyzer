const express = require("express");
const cors = require("cors");
const companiesRoutes = require("./routes/companies");
const db = require("./db");

const app = express();
app.use(cors());
app.use(express.json());

// ✅ API Routes
app.use("/api/companies", companiesRoutes);

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
