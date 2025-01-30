import React from "react";
import { Typography, Box } from "@mui/material";

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        width: "100%",
        padding: "1rem",
        backgroundColor: "#1c1c1c",
        color: "white",
        textAlign: "center",
        marginTop: "2rem",
      }}
    >
      <Typography variant="body2">
        © {new Date().getFullYear()} Financial Assistant. All rights reserved.
      </Typography>
    </Box>
  );
};

export default Footer;
