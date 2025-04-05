import React, { useEffect, useState } from "react";
import NavigationBar from "../navBar/Navbar";
import { Box, Typography, Paper, Button, TextField } from "@mui/material";
import BarGraph from "./BarGraph";
import LineGraph from "./LineGraph";
import TreeChart from "./TreeChart";
import CustomPieChart from "./PieChart";

const Exploration = () => {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/birds/species-data/")
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data: ", error));
  }, []);

  return (
    <div>
      <NavigationBar />
      {/* Header with Title in Center & Date Selector on the Right */}
      <Box sx={{ padding: "20px", display: "flex", alignItems: "center" }}>
        {/* Empty box to balance the flex layout */}
        <Box sx={{ flex: 1 }} />

        {/* Title in the center */}
        <Box sx={{ flex: 1, display: "flex", justifyContent: "center" }}>
          <Typography variant="h4" fontWeight="bold">
            Exploration Page
          </Typography>
        </Box>

        {/* Date Selector Positioned to the Right */}
        <Box sx={{ flex: 1, display: "flex", justifyContent: "flex-end", gap: "10px", alignItems: "center" }}>
          <TextField
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            size="small"
          />
          <TextField
            label="End Date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
            size="small"
          />
          <Button variant="contained" color="primary">
            Apply
          </Button>
        </Box>
      </Box>

      <Typography variant="body1" sx={{ textAlign: "center", marginTop: "10px" }}>
        Welcome to the Exploration page! Here you can analyze data and gain insights.
      </Typography>

      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "20px",
          gap: "30px",
        }}
      >
        {/* Bar Chart & Pie Chart */}
        <Box sx={{ display: "flex", justifyContent: "center", gap: "30px", padding: "20px", width: "85%"}}>
        <Paper elevation={3} sx={{ width: "70%", height: "420px", overflow: "hidden" }}>
          <BarGraph />
        </Paper>
          <Paper elevation={3} sx={{ width: "30%", height: "420px", overflow: "hidden" }}>
            <CustomPieChart />
          </Paper>
        </Box>

        {/* Line Chart */}
        <Paper elevation={3} sx={{ width: "80%", height: "400px", padding: "20px", overflow: "hidden" }}>
          <LineGraph />
        </Paper>

        {/* Tree Chart */}
        <Paper elevation={3} sx={{ width: "80%", height: "400px", padding: "20px", overflow: "hidden" }}>
            <TreeChart />
          </Paper>
      </Box>
    </div>
  );
};

export default Exploration;
