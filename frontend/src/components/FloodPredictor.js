import React, { useState } from "react";
import axios from "axios";
import { Box, TextField, Button, Typography, Paper, Divider } from "@mui/material";
import RiskMeter from "./RiskMeter";

const FloodPredictor = () => {
  const [location, setLocation] = useState("");
  const [rainfall, setRainfall] = useState("");
  const [risk, setRisk] = useState(null);

  const predict = async () => {
    try {
      const res = await axios.post("http://localhost:8000/api/predict-flood/", {
        location,
        rainfall: parseFloat(rainfall),
      });
      setRisk(res.data.flood_risk);
    } catch (err) {
      console.error(err);
      setRisk("Error: Invalid input or server issue");
    }
  };

  return (
    <Paper
      elevation={6}
      sx={{
        marginLeft: "20px",
        padding: 2,
        maxWidth: 250,
        width: "100%",
        borderRadius: 3,
        background: "#ffffff",
      }}
    >
      <Box sx={{ display: "flex-row", gap: 3, mb: 3, mt: 3 }}>
        <TextField
          label="Location"
          variant="outlined"
          fullWidth
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
        <TextField
          label="Rainfall (mm)"
          variant="outlined"
          fullWidth
          value={rainfall}
          sx={{ mt: 1}}
          onChange={(e) => setRainfall(e.target.value)}
        />
      </Box>

      <Button
        variant="contained"
        color="primary"
        fullWidth
        size="large"
        sx={{ fontWeight: "bold", textTransform: "none" }}
        onClick={predict}
      >
        Get Flood Risk
      </Button>

      <Box mt={5} textAlign="center" align items="center">
        <RiskMeter risk={risk} />
      </Box>
    </Paper>
  );
};

export default FloodPredictor;