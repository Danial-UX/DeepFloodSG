import { useState, useEffect } from "react";
import {
  Autocomplete,
  TextField,
  CircularProgress,
  Stack,
  IconButton,
  Divider,
} from "@mui/material";
import DirectionsOutlinedIcon from '@mui/icons-material/DirectionsOutlined';
import { handleSearch } from "../utils/onemap";

export default function SearchBar({ label, onSelect, value, setValue = () => {}, onSwap }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearchChange = async (value) => {
    setLoading(true);
    await handleSearch(value, (res) => {
      setResults(res);
      setLoading(false);
    });
  };

  useEffect(() => {
    if (value) {
      handleSearchChange(value);
    }
  }, [value]);

  return (
    <Stack spacing={1}>
      <Autocomplete
        freeSolo
        options={results}
        value={value}
        onInputChange={(_, newValue, reason) => {
          if (reason === "input") {
            setValue(newValue);
            handleSearchChange(newValue);
          }
        }}
        onChange={(_, selected) => {
          if (selected) {
            setValue(selected.ADDRESS);
            onSelect(selected);
          }
        }}
        getOptionLabel={(option) => option.ADDRESS || option}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            variant="outlined"
            size="small"
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {loading ? <CircularProgress size={18} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderColor: "#007bff",
                },
                "&:hover fieldset": {
                  borderColor: "#0056b3",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#007bff",
                },
              },
            }}
          />
        )}
      />
      {onSwap && (
        <Stack direction="row" alignItems="center">
          <Divider sx={{ flexGrow: 1 }} />
          <IconButton onClick={onSwap}>
            <DirectionsOutlinedIcon />
          </IconButton>
          <Divider sx={{ flexGrow: 1 }} />
        </Stack>
      )}
    </Stack>
  );
}
