import React from "react";
import { AppBar, Toolbar, Typography, Button } from "@mui/material";

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Financial Assistant
        </Typography>
        <Button color="inherit">Home</Button>
        <Button color="inherit">Dashboard</Button>
        <Button color="inherit">Settings</Button>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
