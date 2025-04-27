import React, { useEffect, useState } from "react";
import Navbar from "../navBar/Navbar";
import Table from "./Table";
import { Button, Box, Dialog, DialogActions, DialogContent, DialogTitle, TextField } from "@mui/material";
import { loadDevicesGeojson } from "./devices.ts";
import FloodPredictor from "../components/FloodPredictor.js";
import Map from "../components/Map.jsx";
import MapWithWalkways from "../components/MapWithWalkways.js";

const Main = () => {
  const [selectedRows, setSelectedRows] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [geojsonData, setGeojsonData] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState("");
  const [visibleFeatures, setVisibleFeatures] = useState([]);

  const handleExportClick = () => {
    if (selectedRows.length === 0) {
      alert("No rows selected for export.");
      return;
    }
    setOpenDialog(true);
  };

  const handleConfirmExport = () => {
    // Convert data to CSV
    const csvContent = [
      ["ID", "Name", "Status", "Longitude", "Latitude"],
      ...selectedRows.map((row) => [row.id, row.name, row.status, row.longditude, row.latitude]),
    ]
      .map((e) => e.join(","))
      .join("\n");

    // Create and download CSV file
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "exported_data.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    setOpenDialog(false);
  };


  // 300 milisecond timeout after state change before updating table
  const handleVisibleFeaturesChange = (features) => {
    clearTimeout(handleVisibleFeaturesChange.timeoutId);
    handleVisibleFeaturesChange.timeoutId = setTimeout(() => {
      setVisibleFeatures(features);
    }, 300);
  };

  // Filter visible features only
  const filteredFeatures = (!statusFilter && !searchQuery) ? visibleFeatures:
  visibleFeatures.filter((feature) => {
    const statusMatch = statusFilter === "" || feature.properties.status === statusFilter;
    // console.log("statusMatch: ", statusMatch);
    // console.log("feature.status: ", feature.properties.status);
    const searchMatch =
      feature.properties.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      feature.properties.status.toLowerCase().includes(searchQuery.toLowerCase());
    // console.log("searchMatch: ", searchMatch);
    // console.log("feature.name: ", feature.properties.name);
    return statusMatch && searchMatch;
  });


  return (
    <div>
      <Navbar />
      <h1 style={{ paddingLeft: "30px" }}>Welcome</h1>
      <Box sx={{ display: "flex", flexDirection: "row", marginLeft: "30px", paddingTop: "10px", width: "70vw" }}>
        <Box sx={{flex:1,  width: "80vw" }}>
          {/* <MapWithWalkways /> */}
          <Map/>
        </Box>
        <FloodPredictor />
      </Box>
      <Box sx={{ display: "flex", justifyContent: "flex-end", paddingTop: "10px", width: "72vw" }}>
        <Button variant="contained" color="primary" onClick={handleExportClick}>
          Export Data
        </Button>
      </Box>

      <Table geojsonFeaturesArray={filteredFeatures || []}
        onSelectionChange={setSelectedRows}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        searchQuery={searchQuery}
        onSearchQueryChange={setSearchQuery}/>
      {/* Confirmation Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Confirm Export</DialogTitle>
        <DialogContent>
          <p>Are you sure you want to export {selectedRows.length} row(s)?</p>
          <TextField
            label="Start Date"
            type="date"
            fullWidth
            InputLabelProps={{ shrink: true }}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            sx={{ marginTop: 2 }}
          />
          <TextField
            label="End Date"
            type="date"
            fullWidth
            InputLabelProps={{ shrink: true }}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            sx={{ marginTop: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleConfirmExport} color="primary" variant="contained">
            Export
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Main;
