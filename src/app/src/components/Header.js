import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";

const Header = () => {
  return (
    <AppBar
      position="absolute"
      sx={{
        background: "transparent",
        boxShadow: "none",
        width: "100%",
        zIndex: 2,
        padding: "0.5rem 1rem",
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between" }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: "bold",
            color: "white",
            textShadow: "0px 0px 5px rgba(255, 255, 255, 0.5)",
          }}
        >
          Financial Assistant
        </Typography>
        <Box>
          <Button
            variant="outlined"
            sx={{
              color: "white",
              borderColor: "white",
              marginRight: "1rem",
              "&:hover": {
                backgroundColor: "rgba(255, 255, 255, 0.1)",
              },
            }}
          >
            Sign In
          </Button>
          <Button
            variant="contained"
            sx={{
              backgroundColor: "#36A2EB",
              "&:hover": {
                backgroundColor: "#1c82d0",
              },
            }}
          >
            Sign Up
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
