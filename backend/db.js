const mysql = require("mysql2");
require("dotenv").config();

const db = mysql.createConnection({
  host: process.env.DB_HOST || "localhost",
  user: process.env.DB_USER || "root",
  password: process.env.DB_PASSWORD || "",
  database: process.env.DB_NAME || "ml_analysis",
});

db.connect((err) => {
  if (err) {
    console.error("DB Connection Failed:", err.stack);
    return;
  }
  console.log("Connected to MySQL as id " + db.threadId);
});

module.exports = db.promise();
