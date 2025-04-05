import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Box, FormGroup, FormControlLabel, Checkbox, Typography } from "@mui/material";

const BarGraph = () => {

  const [data, setData] = useState([]);
  // const [selectedBird, setSelectedBird] = useState([]);
  const[formattedData, setFormattedData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/birds/species-count/")
    .then((response) => response.json())
    .then((data) => { 
      // console.log(data);
      setData(data);
      const formatted = (data.map((item) => ({
        name: item["commonName"],
        count: item["count"],
      })));
      // console.log(formatted);
      setFormattedData(formatted);
      // setSelectedBird(formatted.map((d) => d.name));
  })
    .catch((error) => console.error("Error fetching data: ", error));
  }, []);


  // const handleToggle = (bird) => {
  //   setSelectedBird((prevSelected) =>
  //     prevSelected.includes(bird)
  //       ? prevSelected.filter((b) => b !== bird)
  //       : [...prevSelected, bird]
  //   );
  // };

  // const filteredData = formattedData.filter((d) =>
  //   selectedBird.includes(d.name)
  // );

  return (
    <Box sx={{ textAlign: "center", padding: "20px", height: "400px" }}>
      <Typography variant="h6" fontWeight="bold" sx={{ marginBottom: "10px" }}>
        Distribution of Bird Species
        </Typography>
      {/* <FormGroup row sx={{ justifyContent: "center", marginBottom: "20px" }}>
        {data.map((bird) => (
          <FormControlLabel
            key={bird["Common Name"]}
            // control={
            //   <Checkbox
            //     checked={selectedBird.includes(bird["Common Name"])}
            //     onChange={() => handleToggle(bird["Common Name"])}
            //   />
            // }
            label={bird["Common Name"]}
          />
        ))}
      </FormGroup> */}

      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={formattedData} margin={{ top: 20, right: 30, left: 20, bottom: 30 }}>
          <XAxis dataKey="name" angle={-45} textAnchor="end" fontSize="10px" interval={0} height={80} />
          <YAxis />
          <Tooltip />
          <Legend verticalAlign="top" align="center"/>
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default BarGraph;
