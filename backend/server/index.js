const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 5000;

// Token Retrieval
app.post('/api/token', async (req, res) => {
  try {
    const { data } = await axios.post('https://www.onemap.gov.sg/api/auth/post/getToken', {
      email: process.env.ONEMAP_EMAIL,
      password: process.env.ONEMAP_PASSWORD
    });
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Token fetch failed' });
  }
});

// Route Retrieval
app.get('/api/route', async (req, res) => {
  try {
    const { start, end, token } = req.query;
    const routeUrl = `https://www.onemap.gov.sg/api/public/routingsvc/route?start=${start}&end=${end}&routeType=walk&token=${token}`;
    const { data } = await axios.get(routeUrl);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Route fetch failed' });
  }
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
