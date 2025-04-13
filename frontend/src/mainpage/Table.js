import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { Box, Select, MenuItem, FormControl, InputLabel, TextField } from "@mui/material";
// import axios from "axios";

const columns = [
  { field: "date", headerName: "Date", flex: 1 },
  { field: "time", headerName: "Time", flex: 1 },
  { field: "location", headerName: "Location", flex: 1 },
  { field: "rainfall", headerName: "Rainfall", flex: 1 },
  { field: "risk", headerName: "Risk", flex: 1 },
  // { field: "id", headerName: "ID", flex: 1 },
  // { field: "name", headerName: "Name", flex: 2 },
  // { field: "type", headerName: "Type", flex: 1 },
  // { field: "status", headerName: "Status", flex: 2 },
  // { field: "longditude", headerName: "Longitude", flex: 1 }, // Do NOT change the spelling
  // { field: "latitude", headerName: "Latitude", flex: 1 },
];

const Table = ({ geojsonFeaturesArray, onSelectionChange, statusFilter, onStatusFilterChange, searchQuery, onSearchQueryChange, }) => {
  const [rows, setRows] = useState([]);
  const [,setSelectedRowIds] = useState([]); // Track selected row IDs

  useEffect(() => {
    if (geojsonFeaturesArray) {
      // console.log("GeoJSON data loaded");
      setRows(geojsonFeaturesArray.map((feature) => ({
        id: feature.id,
        name: feature.properties.name,
        status: feature.properties.status,
        longditude: feature.geometry.coordinates[0],
        latitude: feature.geometry.coordinates[1],
      })));
    } else {
      setRows([]);
      // console.log("Invalid GeoJSON data");
    }
  }, [geojsonFeaturesArray]);

  // Handle row selection
  const handleSelectionChange = (selection) => {
    setSelectedRowIds(selection);
    const selectedRows = rows.filter((row) => selection.includes(row.id));
    onSelectionChange(selectedRows);
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", alignItems: "flex-start", marginTop: "20px" }}> 
      <Box sx={{ width: "65vw", height: "auto", minHeight: 400 }}>
        <Box sx={{ display: "flex", marginBottom: "20px", gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <TextField
              label="Search by Location"
              variant="outlined"
              fullWidth
              value={searchQuery}
              onChange={(e) => onSearchQueryChange(e.target.value)}
            />
          </Box>
          {/* <Box sx={{ flex: 1 }}>
            <FormControl fullWidth>
              <InputLabel id="status-select-label">Status</InputLabel>
              <Select labelId="status-select-label" value={statusFilter} label="Status" onChange={(e) => onStatusFilterChange(e.target.value)}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Box> */}
        </Box>

        <DataGrid
          rows={rows}
          columns={columns}
          autoHeight
          checkboxSelection
          disableColumnMenu
          onRowSelectionModelChange={handleSelectionChange} // Track selected rows
        />
      </Box>
    </Box>
  );
};

export default Table;
