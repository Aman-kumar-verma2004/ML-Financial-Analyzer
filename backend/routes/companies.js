const express = require("express");
const router = express.Router();
const { getAllCompanies, getCompanyById } = require("../controllers/companyController");

router.get("/", getAllCompanies);       // ✅ All companies
router.get("/:id", getCompanyById);     // ✅ Single company

module.exports = router;
