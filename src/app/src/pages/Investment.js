import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Avatar,
  AppBar,
  Toolbar,
  CircularProgress,
} from "@mui/material";
import { Link } from "react-router-dom";
import SendIcon from "@mui/icons-material/Send";

const navItems = [
  { name: "ClassifyBot 💡", path: "/dashboard" },
  { name: "Optimization", path: "/optimization" },
  { name: "Investment", path: "/investment" },
  { name: "News", path: "/FinancialNews" },
];

const FinancialQA = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  const sendMessage = () => {
    if (!input.trim()) return;
    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    // Fake chatbot response (replace with your real API call)
    setTimeout(() => {
      const botMessage = {
        text: `Here's a suggestion based on "${userMessage.text}" — consider creating a weekly budget!`,
        sender: "bot",
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1500);
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <Box
      sx={{
        width: "100%",
        background: "radial-gradient(circle, #888888, #444444, #1c1c1c)",
        color: "white",
        minHeight: "100vh",
      }}
    >
      {/* ✅ Fixed Top Nav */}
      <AppBar
        position="fixed"
        sx={{
          backgroundColor: "transparent",
          boxShadow: "none",
          padding: "0.5rem 1rem",
        }}
      >
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", color: "white" }}>
            Financial Assistant
          </Typography>
          <Box>
            {navItems.map((item) => (
              <Button
                key={item.name}
                component={Link}
                to={item.path}
                variant="text"
                sx={{
                  color: "white",
                  position: "relative",
                  "&:hover": {
                    color: "#ADD8E6",
                    "&::after": {
                      content: '""',
                      position: "absolute",
                      width: "100%",
                      height: "2px",
                      bottom: 0,
                      left: 0,
                      backgroundColor: "#ADD8E6",
                      visibility: "visible",
                      transform: "scaleX(1)",
                      transition: "all 0.3s ease-in-out",
                    },
                  },
                  "&::after": {
                    content: '""',
                    position: "absolute",
                    width: "100%",
                    height: "2px",
                    bottom: 0,
                    left: 0,
                    backgroundColor: "#ADD8E6",
                    visibility: "hidden",
                    transform: "scaleX(0)",
                    transition: "all 0.3s ease-in-out",
                  },
                }}
              >
                {item.name}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </AppBar>

      {/* ✅ Main Chat Body */}
      <Box
        sx={{
          pt: "100px", // offset for AppBar
          maxWidth: "800px",
          mx: "auto",
          px: 2,
          display: "flex",
          flexDirection: "column",
          minHeight: "calc(100vh - 100px)",
        }}
      >
        {/* Chat Box */}
        <Box
          sx={{
            flexGrow: 1,
            overflowY: "auto",
            mb: 2,
            display: "flex",
            flexDirection: "column",
            backgroundColor: "#2f2f2f",
            borderRadius: "16px",
            p: 3,
            boxShadow: "0px 6px 16px rgba(0,0,0,0.3)",
          }}
        >
          {messages.map((msg, i) => (
            <Box
              key={i}
              sx={{
                display: "flex",
                justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
                mb: 1,
              }}
            >
              {msg.sender === "bot" && <Avatar sx={{ mr: 1 }}>🤖</Avatar>}
              <Box
                sx={{
                  backgroundColor: msg.sender === "user" ? "#1976d2" : "#555",
                  color: "white",
                  px: 2,
                  py: 1.5,
                  borderRadius:
                    msg.sender === "user"
                      ? "12px 12px 0 12px"
                      : "12px 12px 12px 0",
                  maxWidth: "75%",
                }}
              >
                <Typography sx={{ fontSize: "14px" }}>{msg.text}</Typography>
              </Box>
            </Box>
          ))}
          {isTyping && (
            <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
              <Avatar sx={{ mr: 1 }}>🤖</Avatar>
              <Typography sx={{ fontStyle: "italic", color: "#ccc" }}>
                Typing...
              </Typography>
            </Box>
          )}
          <div ref={chatEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Ask a financial question..."
            variant="outlined"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            sx={{
              input: { color: "white" },
              backgroundColor: "#1e1e1e",
              borderRadius: "10px",
              mr: 2,
              "& .MuiOutlinedInput-notchedOutline": { borderColor: "#444" },
              "&:hover .MuiOutlinedInput-notchedOutline": {
                borderColor: "#888",
              },
            }}
          />
          <Button
            onClick={sendMessage}
            variant="contained"
            color="primary"
            sx={{ minWidth: "48px" }}
          >
            <SendIcon />
          </Button>
        </Box>

        <Button
          variant="outlined"
          color="secondary"
          onClick={clearChat}
          sx={{
            alignSelf: "center",
            mb: 3,
            color: "#fff",
            borderColor: "#ccc",
            "&:hover": {
              borderColor: "#f50057",
              backgroundColor: "#ff1744",
              color: "#fff",
            },
          }}
        >
          🗑️ Clear Chat
        </Button>
      </Box>
    </Box>
  );
};

export default FinancialQA;
