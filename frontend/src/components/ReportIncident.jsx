import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  FormControl,
  FormLabel,
  TextField,
  Input,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

const ReportIncident = () => {
  const navigate = useNavigate();
  const [responses, setResponses] = useState({
    location: "",
    seenFlood: "",
    waterLevel: "",
    damageExtent: "",
    roadBlocked: "",
    floodImage: null, // To store the uploaded image
  });

  const handleChange = (event) => {
    setResponses({
      ...responses,
      [event.target.name]: event.target.value,
    });
  };

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setResponses({
        ...responses,
        floodImage: file,
      });
    }
  };

  const handleSubmit = () => {
    // Here you would normally submit the form data and image to a backend server
    console.log("Submitted Responses:", responses);
    alert("Thank you for your feedback!");
    navigate("/"); // Navigate to the main page after submission
  };

  return (
    <Paper
      elevation={5}
      sx={{
        maxWidth: 600,
        margin: "40px auto",
        padding: 4,
        borderRadius: 3,
      }}
    >
      <Typography variant="h4" gutterBottom>
        Flood Incident Report
      </Typography>

      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        Please provide the location of the flood:
      </Typography>
      <TextField
        fullWidth
        label="Flood Location"
        name="location"
        value={responses.location}
        onChange={handleChange}
        sx={{ mb: 3 }}
      />

      <Box sx={{ mt: 3 }}>
        <FormControl component="fieldset" sx={{ mb: 3 }}>
          <FormLabel>1. Did you personally witness flooding in your area today?</FormLabel>
          <RadioGroup name="seenFlood" value={responses.seenFlood} onChange={handleChange}>
            <FormControlLabel value="yes" control={<Radio />} label="Yes" />
            <FormControlLabel value="no" control={<Radio />} label="No" />
          </RadioGroup>
        </FormControl>

        <FormControl component="fieldset" sx={{ mb: 3 }}>
          <FormLabel>2. At its deepest point, how would you describe the floodwater depth?</FormLabel>
          <RadioGroup name="waterLevel" value={responses.waterLevel} onChange={handleChange}>
            <FormControlLabel value="ankle" control={<Radio />} label="Ankle-deep" />
            <FormControlLabel value="knee" control={<Radio />} label="Knee-deep" />
            <FormControlLabel value="waist" control={<Radio />} label="Waist-deep or higher" />
          </RadioGroup>
        </FormControl>

        <FormControl component="fieldset" sx={{ mb: 3 }}>
          <FormLabel>3. Did the flood cause any damage to properties or infrastructure?</FormLabel>
          <RadioGroup name="damageExtent" value={responses.damageExtent} onChange={handleChange}>
            <FormControlLabel value="none" control={<Radio />} label="No damage" />
            <FormControlLabel value="minor" control={<Radio />} label="Minor damage" />
            <FormControlLabel value="severe" control={<Radio />} label="Severe damage" />
          </RadioGroup>
        </FormControl>

        <FormControl component="fieldset" sx={{ mb: 3 }}>
          <FormLabel>4. Were any roads or walkways obstructed by floodwaters or debris?</FormLabel>
          <RadioGroup name="roadBlocked" value={responses.roadBlocked} onChange={handleChange}>
            <FormControlLabel value="no" control={<Radio />} label="No" />
            <FormControlLabel value="some" control={<Radio />} label="Some areas" />
            <FormControlLabel value="yes" control={<Radio />} label="Yes, completely" />
          </RadioGroup>
        </FormControl>

        {/* Image Upload Section */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            5. Please upload a picture of the flood (if available):
          </Typography>
          <Input
            type="file"
            name="floodImage"
            onChange={handleImageChange}
            inputProps={{ accept: "image/*" }} // Only accept image files
            sx={{ mb: 3 }}
          />
          {responses.floodImage && (
            <Typography variant="body2" color="textSecondary">
              {responses.floodImage.name} selected
            </Typography>
          )}
        </Box>

        <Button
          variant="contained"
          color="primary"
          sx={{ mt: 2 }}
          fullWidth
          onClick={handleSubmit}
        >
          Submit Report
        </Button>
      </Box>
    </Paper>
  );
};

export default ReportIncident;
