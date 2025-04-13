import React from "react";
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import { Box, Typography } from "@mui/material";

const RiskGauge = ({ risk }) => {
  const percentage = Math.round(risk * 100);

  const data = [
    { name: "risk", value: percentage, fill:
      percentage < 33
        ? "#4caf50" // green
        : percentage < 66
        ? "#ffeb3b" // yellow
        : "#f44336" // red
    },
  ];

  return (
    <Box sx={{ width: 180, height: 180, textAlign: "center", backgroundColor: "#222", borderRadius: 2, padding: 2 }}>
    <Box sx={{ marginTop: "-40px", height: 150 }}>
        <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
            cx="50%"
            cy="100%"
            innerRadius="80%"
            outerRadius="100%"
            startAngle={180}
            endAngle={0}
            barSize={20}
            data={data}
        >
            <PolarAngleAxis
            type="number"
            domain={[0, 100]}
            tickCount={6}
            angleAxisId={0}
            tick={{ fill: "#ccc", fontSize: 12 }}
            axisLine={false}
            />
            <RadialBar background clockWise dataKey="value" />
        </RadialBarChart>
        </ResponsiveContainer>
    </Box>
      <Typography variant="h4" fontWeight="bold" color="white">
        {percentage}%
      </Typography>
      <Typography color="white">
        Flood Risk Chance
      </Typography>
    </Box>
  );
};

export default RiskGauge;