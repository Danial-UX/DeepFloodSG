import React from "react";
import { ResponsiveContainer, Treemap } from "recharts";
import { Box, Typography } from "@mui/material";

// Dummy data for the tree chart
const data = [
  { name: "Bird Type A", size: 400 },
  { name: "Bird Type B", size: 300 },
  { name: "Bird Type C", size: 200 },
  { name: "Bird Type D", size: 150 },
  { name: "Bird Type E", size: 100 },
];

const TreeChart = () => {
  return (
    <Box sx={{ width: "100%", height: "100%" }}> 
      <Typography variant="h6" fontWeight="bold" sx={{ marginBottom: "10px" }}>
        Bird Detection Tree Chart
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <Treemap
          width={400}
          height={300}
          data={data}
          dataKey="size"
          stroke="#fff"
          fill="#7B68EE"
        />
      </ResponsiveContainer>
    </Box>
  );
};

export default TreeChart;
