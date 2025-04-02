// import React, { useState, useEffect, useRef } from "react";
// import {
//   Box,
//   Button,
//   TextField,
//   Typography,
//   Avatar,
//   AppBar,
//   Toolbar,
//   CircularProgress,
// } from "@mui/material";
// import { Link } from "react-router-dom";
// import SendIcon from "@mui/icons-material/Send";

// const navItems = [
//   { name: "ClassifyBot 💡", path: "/dashboard" },
//   { name: "Optimization", path: "/optimization" },
//   { name: "Investment", path: "/investment" },
//   { name: "News", path: "/FinancialNews" },
// ];

// const FinancialQA = () => {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");
//   const [isTyping, setIsTyping] = useState(false);
//   const [estimatedSavings, setEstimatedSavings] = useState(0);
//   const chatEndRef = useRef(null);

//   const sendMessage = () => {
//     if (!input.trim()) return;
//     const userMessage = { text: input, sender: "user" };
//     setMessages((prev) => [...prev, userMessage]);
//     setInput("");
//     setIsTyping(true);

//     setTimeout(() => {
//       const botMessage = {
//         text: `Here's a suggestion based on "${userMessage.text}" — consider creating a weekly budget!`,
//         sender: "bot",
//       };
//       setMessages((prev) => [...prev, botMessage]);
//       setIsTyping(false);
//     }, 1500);
//   };

//   const clearChat = () => {
//     setMessages([]);
//   };

//   useEffect(() => {
//     chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   useEffect(() => {
//     const stored = localStorage.getItem("estimatedSavings");
//     if (stored) setEstimatedSavings(parseFloat(stored));
//   }, []);

//   return (
//     <Box
//       sx={{
//         width: "100%",
//         background: "radial-gradient(circle, #888888, #444444, #1c1c1c)",
//         color: "white",
//         minHeight: "100vh",
//       }}
//     >
//       {/* ✅ Top AppBar */}
//       <AppBar
//         position="fixed"
//         sx={{ backgroundColor: "transparent", boxShadow: "none", padding: "0.5rem 1rem" }}
//       >
//         <Toolbar sx={{ justifyContent: "space-between" }}>
//           <Typography variant="h6" sx={{ fontWeight: "bold", color: "white" }}>
//             Financial Assistant
//           </Typography>
//           <Box>
//             {navItems.map((item) => (
//               <Button
//                 key={item.name}
//                 component={Link}
//                 to={item.path}
//                 variant="text"
//                 sx={{
//                   color: "white",
//                   position: "relative",
//                   "&:hover": {
//                     color: "#ADD8E6",
//                     "&::after": {
//                       content: '""',
//                       position: "absolute",
//                       width: "100%",
//                       height: "2px",
//                       bottom: 0,
//                       left: 0,
//                       backgroundColor: "#ADD8E6",
//                       visibility: "visible",
//                       transform: "scaleX(1)",
//                       transition: "all 0.3s ease-in-out",
//                     },
//                   },
//                   "&::after": {
//                     content: '""',
//                     position: "absolute",
//                     width: "100%",
//                     height: "2px",
//                     bottom: 0,
//                     left: 0,
//                     backgroundColor: "#ADD8E6",
//                     visibility: "hidden",
//                     transform: "scaleX(0)",
//                     transition: "all 0.3s ease-in-out",
//                   },
//                 }}
//               >
//                 {item.name}
//               </Button>
//             ))}
//           </Box>
//         </Toolbar>
//       </AppBar>

//       {/* ✅ Main Chat & Investment Display */}
//       <Box
//         sx={{
//           pt: "100px",
//           maxWidth: "800px",
//           mx: "auto",
//           px: 2,
//           display: "flex",
//           flexDirection: "column",
//           minHeight: "calc(100vh - 100px)",
//         }}
//       >
//         {/* 🧠 Chat Messages */}
//         <Box
//           sx={{
//             flexGrow: 1,
//             overflowY: "auto",
//             mb: 2,
//             display: "flex",
//             flexDirection: "column",
//             backgroundColor: "#2f2f2f",
//             borderRadius: "16px",
//             p: 3,
//             boxShadow: "0px 6px 16px rgba(0,0,0,0.3)",
//           }}
//         >
//           {messages.map((msg, i) => (
//             <Box
//               key={i}
//               sx={{
//                 display: "flex",
//                 justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
//                 mb: 1,
//               }}
//             >
//               {msg.sender === "bot" && <Avatar sx={{ mr: 1 }}>🤖</Avatar>}
//               <Box
//                 sx={{
//                   backgroundColor: msg.sender === "user" ? "#1976d2" : "#555",
//                   color: "white",
//                   px: 2,
//                   py: 1.5,
//                   borderRadius: msg.sender === "user" ? "12px 12px 0 12px" : "12px 12px 12px 0",
//                   maxWidth: "75%",
//                 }}
//               >
//                 <Typography sx={{ fontSize: "14px" }}>{msg.text}</Typography>
//               </Box>
//             </Box>
//           ))}
//           {isTyping && (
//             <Box sx={{ display: "flex", alignItems: "center", mt: 1, gap: 1 }}>
//               <Avatar>🤖</Avatar>
//               <Typography sx={{ fontStyle: "italic", color: "#ccc" }}>Typing...</Typography>
//               <CircularProgress size={20} sx={{ color: "#ccc" }} />
//             </Box>
//           )}
//           <div ref={chatEndRef} />
//         </Box>

//         {/* 💬 Input Field */}
//         <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
//           <TextField
//             fullWidth
//             placeholder="Ask a financial question..."
//             variant="outlined"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             onKeyDown={(e) => e.key === "Enter" && sendMessage()}
//             sx={{
//               input: { color: "white" },
//               backgroundColor: "#1e1e1e",
//               borderRadius: "10px",
//               mr: 2,
//               "& .MuiOutlinedInput-notchedOutline": { borderColor: "#444" },
//               "&:hover .MuiOutlinedInput-notchedOutline": {
//                 borderColor: "#888",
//               },
//             }}
//           />
//           <Button onClick={sendMessage} variant="contained" color="primary" sx={{ minWidth: "48px" }}>
//             <SendIcon />
//           </Button>
//         </Box>

//         {/* 💸 Investment Display */}
//         <Box
//         sx={{
//           mt: 3,
//           px: 2,
//           py: 1.5,
//           borderRadius: "10px",
//           background: "linear-gradient(135deg, #9be15d, #00e3ae)",
//           textAlign: "center",
//           boxShadow: "0px 4px 12px rgba(0,0,0,0.3)",
//           maxWidth: "300px",
//           mx: "auto",
//         }}
//       >
//         <Typography variant="subtitle1" sx={{ fontWeight: "bold", color: "#003b2f", mb: 0.5 }}>
//           💸 Amount You Can Invest
//         </Typography>
//         <Typography variant="h5" sx={{ fontWeight: "bold", color: "#003b2f" }}>
//           ${estimatedSavings.toFixed(2)}
//         </Typography>
//       </Box>


//         {/* 🗑️ Clear Button */}
//         <Button
//           variant="outlined"
//           color="secondary"
//           onClick={clearChat}
//           sx={{
//             alignSelf: "center",
//             mt: 4,
//             mb: 3,
//             color: "#fff",
//             borderColor: "#ccc",
//             "&:hover": {
//               borderColor: "#f50057",
//               backgroundColor: "#ff1744",
//               color: "#fff",
//             },
//           }}
//         >
//           🗑️ Clear Chat
//         </Button>
//       </Box>
//     </Box>
//   );
// };

// export default FinancialQA;



import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  Box, Typography, TextField, Paper, Divider,
  CircularProgress, List, ListItem, ListItemText,
  Chip, Avatar, IconButton, Tooltip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const ChatContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  height: '80vh',
  maxWidth: 800,
  margin: '0 auto',
  padding: theme.spacing(2),
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[3],
}));

const MessageBubble = styled(Paper)(({ theme, type }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1),
  maxWidth: '75%',
  marginLeft: type === 'user' ? 'auto' : 'initial',
  backgroundColor: type === 'user' ? theme.palette.primary.main : theme.palette.grey[100],
  color: type === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
  borderRadius: type === 'user' ? '18px 18px 0 18px' : '18px 18px 18px 0',
}));

export default function FinancialChatBot() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stocks, setStocks] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    setMessages([{
      type: 'bot',
      text: 'Hello! I can analyze stocks. Ask about AAPL, MSFT, GOOG, AMZN, TSLA, JPM, NVDA, or WMT',
      time: new Date().toLocaleTimeString()
    }]);
    
    axios.get('http://localhost:5001/api/stocks')
      .then(res => setStocks(res.data.tickers))
      .catch(console.error);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    
    const userMessage = {
      type: 'user',
      text: input,
      time: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      const ticker = input.toUpperCase().match(/\b[A-Z]{2,4}\b/)?.[0] || '';
      if (!stocks.includes(ticker)) {
        throw new Error(`We don't support ${ticker} yet. Try one of: ${stocks.join(', ')}`);
      }
      
      const res = await axios.get('http://localhost:5001/api/analyze', { params: { ticker } });
      
      setMessages(prev => [...prev, {
        type: 'bot',
        text: `Analysis for ${ticker}:`,
        data: res.data,
        time: new Date().toLocaleTimeString()
      }]);
      
    } catch (err) {
      setMessages(prev => [...prev, {
        type: 'bot',
        text: err.response?.data?.error || err.message,
        isError: true,
        time: new Date().toLocaleTimeString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = (message) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
      <Avatar sx={{ 
        bgcolor: message.type === 'user' ? 'primary.main' : 'secondary.main',
        width: 32, height: 32
      }}>
        {message.type === 'user' ? <AccountCircleIcon /> : <SmartToyIcon />}
      </Avatar>
      
      <MessageBubble type={message.type}>
        <Typography>{message.text}</Typography>
        
        {message.data && (
          <>
            <Divider sx={{ my: 1 }} />
            <List dense>
              <ListItem>
                <Chip 
                  label={`${message.data.prediction.toUpperCase()} (${(message.data.confidence * 100).toFixed(1)}%)`}
                  color={message.data.prediction === 'up' ? 'success' : 'error'} 
                  size="small" 
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary={`Price: $${message.data.price.toFixed(2)}`}
                  secondary={`RSI: ${message.data.rsi.toFixed(1)}`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary={`SMA10: $${message.data.sma_10.toFixed(2)}`}
                  secondary={`EMA50: $${message.data.ema_50.toFixed(2)}`}
                />
              </ListItem>
              {message.data.pe_ratio && (
                <ListItem>
                  <ListItemText
                    primary={`P/E: ${message.data.pe_ratio.toFixed(2)}`}
                    secondary={`Yield: ${message.data.dividend_yield ? (message.data.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}`}
                  />
                </ListItem>
              )}
            </List>
          </>
        )}
        <Typography variant="caption" sx={{ display: 'block', textAlign: 'right', opacity: 0.7 }}>
          {message.time}
        </Typography>
      </MessageBubble>
    </Box>
  );

  return (
    <ChatContainer>
      <Box display="flex" alignItems="center" mb={2}>
        <SmartToyIcon color="primary" sx={{ mr: 1 }} />
        <Typography variant="h6">Financial Advisor</Typography>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      <Box sx={{ flex: 1, overflow: 'auto', mb: 2 }}>
        {messages.map((msg, i) => (
          <div key={i}>{renderMessage(msg)}</div>
        ))}
        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" gap={1}>
            <CircularProgress size={20} />
            <Typography>Analyzing..</Typography>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>
      
      <Box display="flex" gap={1}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Ask about a stock (e.g. AAPL)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          disabled={loading}
        />
        <IconButton 
          color="primary" 
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </ChatContainer>
  );
}