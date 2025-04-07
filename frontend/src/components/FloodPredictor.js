import React, { useState } from "react";
import axios from "axios";
import { Box, TextField, Button } from "@mui/material";

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
    <Box sx={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", marginTop: "20px" }}>
        <Box sx={{ display: "flex", marginBottom: "20px", gap: 2 }}>
              <Box sx={{ flex: 1 }}>
                <TextField
                  label="Location"
                  variant="outlined"
                  fullWidth
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </Box>
              <Box sx={{ flex: 1 }}>
                <TextField
                  label="Rainfall (mm)"
                  variant="outlined"
                  fullWidth
                  value={rainfall}
                  onChange={(e) => setRainfall(e.target.value)}
                />
              </Box>
            </Box>
            <Button variant="contained" color="primary" onClick={predict}>
                Predict
            </Button>
            {risk !== null && (
                <Box sx={{ marginTop: "20px", textAlign: "center" }}>
                    <h2>Flood Risk Prediction</h2>
                    <p>{risk}</p>
                </Box>
                )}
            </Box>
     )}
        

export default FloodPredictor;