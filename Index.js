const express = require("express");
const axios = require("axios");
const cheerio = require("cheerio");

const app = express();
const PORT = process.env.PORT || 3000;

app.get("/price/:symbol", async (req, res) => {
  try {
    const symbol = req.params.symbol;
    const url = `https://www.euro2day.gr/ase/quotes/${symbol}.html`;
    const response = await axios.get(url);
    const $ = cheerio.load(response.data);
    const priceText = $("td.text-right.last-col").first().text().trim();
    const price = parseFloat(priceText.replace(",", "."));
    
    if (!isNaN(price)) {
      res.json({ symbol, price });
    } else {
      res.status(404).json({ error: "Price not found" });
    }
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch data" });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
