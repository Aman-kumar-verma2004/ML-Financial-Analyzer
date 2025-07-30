const fs = require("fs");
const path = require("path");
const db = require("../db");

// 📂 Local JSON files ka path
const dataDir = path.join(__dirname, "../data");

const getAllCompanies = async (req, res) => {
  try {
    // MySQL se basic info nikalna
    const [rows] = await db.query("SELECT id, company, strngth FROM ml");
    res.json(rows);
  } catch (err) {
    console.error("❌ Error fetching companies:", err);
    res.status(500).json({ error: "Internal Server Error" });
  }
};

const getCompanyById = async (req, res) => {
  const { id } = req.params; // ABB / TCS / INFY etc.

  try {
    // ✅ MySQL se company ke pros & cons laao
    const [rows] = await db.query("SELECT * FROM ml WHERE company = ?", [id]);

    if (rows.length === 0) {
      return res.status(404).json({ error: "Company not found in DB" });
    }

    const companyData = rows[0];

    // ✅ JSON file path
    const jsonPath = path.join(dataDir, `${id}.json`);

    // ✅ JSON file exist check
    if (!fs.existsSync(jsonPath)) {
      return res.status(404).json({ error: "Company JSON file not found" });
    }

    // ✅ JSON file read
    const rawData = fs.readFileSync(jsonPath);
    const jsonDetails = JSON.parse(rawData);

    // ✅ Final response combine: DB + JSON
    res.json({
      ...companyData,
      ...jsonDetails.company, // JSON ka "company" object merge
      pros: companyData.pros ? companyData.pros.split("|") : [],
      cons: companyData.cons ? companyData.cons.split("|") : [],
    });
  } catch (err) {
    console.error(`❌ Error fetching company ${id}:`, err);
    res.status(500).json({ error: "Internal Server Error" });
  }
};

module.exports = { getAllCompanies, getCompanyById };
