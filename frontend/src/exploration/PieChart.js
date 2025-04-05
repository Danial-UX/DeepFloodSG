import React, { useEffect, useState} from "react";
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";
import { Box, Typography } from "@mui/material";


const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

const CustomPieChart = () => {
    const [data, setData] = useState([]);
  
    useEffect(() => {
      fetch("http://localhost:8000/api/birds/species-count/")
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data: ", error));
    }, []);

  return (
    <Box sx={{ width: "100%", height: "100%", padding:"20px", textAlign: "center" }}>
      <Typography variant="h6" fontWeight="bold" sx={{ marginBottom: "10px" }}>
        Pie Chart of Bird Species
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            outerRadius={100}
            fill="#8884d8"
            dataKey="count"
            nameKey="commonName"
            label = {({name, percent}) => 
              `${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default CustomPieChart;
