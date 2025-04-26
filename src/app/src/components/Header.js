import React, { useState } from "react";
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem, Avatar, useTheme } from "@mui/material";
import { Link, useNavigate } from "react-router-dom";
import { styled } from "@mui/material/styles";

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  background: "rgba(0, 0, 0, 0.9)",
  backdropFilter: "blur(10px)",
  boxShadow: "none",
  borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
}));

const StyledButton = styled(Button)(({ theme }) => ({
  color: "#fff",
  textTransform: "none",
  fontWeight: 500,
  fontSize: "1rem",
  padding: "8px 16px",
  borderRadius: "8px",
  fontFamily: "'Inter', sans-serif",
  "&:hover": {
    backgroundColor: "rgba(255, 255, 255, 0.1)",
  },
}));

const StyledLink = styled(Link)(({ theme }) => ({
  textDecoration: "none",
  color: "inherit",
}));

const Header = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const theme = useTheme();

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    navigate("/");
  };

  return (
    <StyledAppBar position="fixed">
      <Toolbar sx={{ justifyContent: "center", px: { xs: 2, md: 4 } }}>
        {/* Left side - Logo */}
        <Box sx={{ position: "absolute", left: { xs: 16, md: 32 } }}>
          <StyledLink to="/">
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                fontSize: "1.5rem",
                color: "#fff",
                letterSpacing: "-0.5px",
                fontFamily: "'Inter', sans-serif",
              }}
            >
              Credge AI
            </Typography>
          </StyledLink>
        </Box>

        {/* Center - Navigation */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <StyledButton component={Link} to="/dashboard">
            Dashboard
          </StyledButton>
          <StyledButton component={Link} to="/optimization">
            Optimization
          </StyledButton>
          <StyledButton component={Link} to="/investment">
            Investment
          </StyledButton>
        </Box>

        {/* Right side - Profile */}
        <Box sx={{ position: "absolute", right: { xs: 16, md: 32 } }}>
          <StyledButton
            component={Link}
            to="/profile"
            sx={{
              display: { xs: "none", md: "flex" },
              alignItems: "center",
              gap: 1,
            }}
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: theme.palette.primary.main,
                fontSize: "1rem",
                fontWeight: 600,
              }}
            >
              U
            </Avatar>
            Profile
          </StyledButton>

          <IconButton
            onClick={handleMenuOpen}
            sx={{
              display: { xs: "flex", md: "none" },
              color: "#fff",
            }}
          >
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: theme.palette.primary.main,
                fontSize: "1rem",
                fontWeight: 600,
              }}
            >
              U
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            PaperProps={{
              sx: {
                mt: 1.5,
                minWidth: 180,
                borderRadius: "12px",
                background: "rgba(0, 0, 0, 0.9)",
                backdropFilter: "blur(10px)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
              },
            }}
          >
            <MenuItem
              component={Link}
              to="/dashboard"
              onClick={handleMenuClose}
              sx={{ 
                py: 1.5,
                color: "#fff",
                fontFamily: "'Inter', sans-serif",
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                }
              }}
            >
              Dashboard
            </MenuItem>
            <MenuItem
              component={Link}
              to="/optimization"
              onClick={handleMenuClose}
              sx={{ 
                py: 1.5,
                color: "#fff",
                fontFamily: "'Inter', sans-serif",
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                }
              }}
            >
              Optimization
            </MenuItem>
            <MenuItem
              component={Link}
              to="/investment"
              onClick={handleMenuClose}
              sx={{ 
                py: 1.5,
                color: "#fff",
                fontFamily: "'Inter', sans-serif",
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                }
              }}
            >
              Investment
            </MenuItem>
            <MenuItem
              component={Link}
              to="/profile"
              onClick={handleMenuClose}
              sx={{ 
                py: 1.5,
                color: "#fff",
                fontFamily: "'Inter', sans-serif",
                "&:hover": {
                  backgroundColor: "rgba(255, 255, 255, 0.1)",
                }
              }}
            >
              Profile
            </MenuItem>
            <MenuItem 
              onClick={handleLogout} 
              sx={{ 
                py: 1.5, 
                color: "#ff4444",
                fontFamily: "'Inter', sans-serif",
                "&:hover": {
                  backgroundColor: "rgba(255, 68, 68, 0.1)",
                }
              }}
            >
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </StyledAppBar>
  );
};

export default Header;
