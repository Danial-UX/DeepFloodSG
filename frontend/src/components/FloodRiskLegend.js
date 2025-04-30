import { Box, Typography } from "@mui/material";

export default function FloodRiskLegend() {
    return (
        <Box
            position="absolute"
            bottom={20}
            right={20}
            zIndex={1000}
            bgcolor="white"
            p={2}
            borderRadius={4}
            boxShadow={3}
        >
            <Typography variant="subtitle2" gutterBottom>
                Flood Risk Legend
            </Typography>
            <Box display="flex" alignItems="center" mb={1}>
                <Box width={20} height={20} bgcolor="red" mr={1} />
                <Typography variant="caption">High Risk (&gt;70%)</Typography>
            </Box>
            <Box display="flex" alignItems="center" mb={1}>
                <Box width={20} height={20} bgcolor="orange" mr={1} />
                <Typography variant="caption">Medium Risk (50-70%)</Typography>
            </Box>
            <Box display="flex" alignItems="center">
                <Box width={20} height={20} bgcolor="yellow" mr={1} />
                <Typography variant="caption">Low Risk (30-50%)</Typography>
            </Box>
        </Box>
    );
}