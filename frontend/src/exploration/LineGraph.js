import React, {useEffect, useState} from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Box, Typography } from "@mui/material";

const LineGraph = () => {

  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/birds/birds-by-device/")
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data: ", error));
  }, []);

  return (
    <Box sx={{ textAlign: "center", padding: "20px" }}>
      <Typography variant="h5" fontWeight="bold">
        Total Birds by Location
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="name"
            tickFormatter={(value) => `${value}`}/>
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="Morning" stroke="#8884d8" strokeWidth={2} name="Morning" />
          <Line type="monotone" dataKey="Evening" stroke="#82ca9d" strokeWidth={2} name="Evening" />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default LineGraph;
