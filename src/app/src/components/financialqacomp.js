// import React, { useState } from 'react';
// import axios from 'axios';
// import { Box, Typography, TextField, Button, Paper, Grid, Divider } from '@mui/material';

// const FinancialChatBot = () => {
//   const [userQuery, setUserQuery] = useState('');
//   const [chatHistory, setChatHistory] = useState([]);  // To store the conversation

//   // Function to handle user question submission
//   const handleUserQuery = async () => {
//     if (userQuery.trim() === '') return;  // Don't submit empty queries

//     // Add user's query to the chat history
//     const newChatHistory = [...chatHistory, { type: 'user', message: userQuery }];
//     setChatHistory(newChatHistory);
//     setUserQuery('');  // Clear the input field

//     try {
//       // Send the query to the Flask backend (Financial QA API)
//       const response = await axios.get('http://localhost:5000/api/financial-qa', {
//         params: { query: userQuery },
//       });

//       // Add the response from the Financial QA agent to the chat history
//       const botResponse = response.data.answer;
//       setChatHistory([...newChatHistory, { type: 'bot', message: botResponse }]);
//     } catch (error) {
//       console.error('Error fetching answer:', error);
//       setChatHistory([
//         ...newChatHistory,
//         { type: 'bot', message: 'Sorry, I couldn’t process that. Please try again.' }
//       ]);
//     }
//   };

//   return (
//     <Box
//       sx={{
//         width: '100%',
//         height: '80vh',
//         maxWidth: 600,
//         margin: '0 auto',
//         backgroundColor: '#2f2f2f',
//         color: 'white',
//         borderRadius: 2,
//         padding: 2,
//         display: 'flex',
//         flexDirection: 'column',
//       }}
//     >
//       {/* Chatbot Header */}
//       <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, textAlign: 'center' }}>
//         Financial Assistant Chatbot
//       </Typography>
//       <Divider sx={{ mb: 2 }} />

//       {/* Chat History */}
//       <Box
//         sx={{
//           flex: 1,
//           overflowY: 'auto',
//           marginBottom: 2,
//           padding: 1,
//           backgroundColor: '#1c1c1c',
//           borderRadius: 1,
//           maxHeight: 'calc(80% - 100px)',
//         }}
//       >
//         {chatHistory.map((message, index) => (
//           <Box key={index} sx={{ marginBottom: 1 }}>
//             <Paper
//               sx={{
//                 padding: 1,
//                 backgroundColor: message.type === 'user' ? '#3f3f3f' : '#444',
//                 maxWidth: '80%',
//                 marginLeft: message.type === 'user' ? 'auto' : 'initial',
//                 marginRight: message.type === 'bot' ? 'auto' : 'initial',
//                 color: 'white',
//               }}
//             >
//               <Typography variant="body1">{message.message}</Typography>
//             </Paper>
//           </Box>
//         ))}
//       </Box>

//       {/* Chat Input */}
//       <Grid container spacing={2}>
//         <Grid item xs={9}>
//           <TextField
//             fullWidth
//             variant="outlined"
//             placeholder="Ask your financial question..."
//             value={userQuery}
//             onChange={(e) => setUserQuery(e.target.value)}
//             sx={{ backgroundColor: '#444', color: 'white' }}
//           />
//         </Grid>
//         <Grid item xs={3}>
//           <Button
//             variant="contained"
//             color="primary"
//             sx={{ height: '100%' }}
//             onClick={handleUserQuery}
//           >
//             Ask
//           </Button>
//         </Grid>
//       </Grid>
//     </Box>
//   );
// };

// export default FinancialChatBot;


// import React, { useState } from 'react';
// import axios from 'axios';
// import { Box, Typography, TextField, Button, Paper, Grid, Divider } from '@mui/material';

// const FinancialChatBot = () => {
//   const [userQuery, setUserQuery] = useState('');
//   const [chatHistory, setChatHistory] = useState([]);  // To store the conversation

//   // Function to handle user question submission
//   const handleUserQuery = async () => {
//     if (userQuery.trim() === '') return;  // Don't submit empty queries

//     // Add user's query to the chat history
//     const newChatHistory = [...chatHistory, { type: 'user', message: userQuery }];
//     setChatHistory(newChatHistory);
//     setUserQuery('');  // Clear the input field

//     try {
//       // Send the query to the Flask backend (Financial QA API)
//       const response = await axios.get('http://localhost:5000/api/financial-qa', {
//         params: { query: userQuery },
//       });

//       // Log the full response to see what data is being returned
//       console.log(response.data);

//       // Handle response correctly, assuming response data contains 'symbol' and 'price' fields
//       const botResponse = response.data.symbol + ": " + response.data.price;  // You can adjust this based on your backend response
//       setChatHistory([...newChatHistory, { type: 'bot', message: botResponse }]);
//     } catch (error) {
//       console.error('Error fetching answer:', error);
//       setChatHistory([
//         ...newChatHistory,
//         { type: 'bot', message: 'Sorry, I couldn’t process that. Please try again.' }
//       ]);
//     }
//   };

//   return (
//     <Box
//       sx={{
//         width: '100%',
//         height: '80vh',
//         maxWidth: 600,
//         margin: '0 auto',
//         backgroundColor: '#2f2f2f',
//         color: 'white',
//         borderRadius: 2,
//         padding: 2,
//         display: 'flex',
//         flexDirection: 'column',
//       }}
//     >
//       {/* Chatbot Header */}
//       <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, textAlign: 'center' }}>
//         Financial Assistant Chatbot
//       </Typography>
//       <Divider sx={{ mb: 2 }} />

//       {/* Chat History */}
//       <Box
//         sx={{
//           flex: 1,
//           overflowY: 'auto',
//           marginBottom: 2,
//           padding: 1,
//           backgroundColor: '#1c1c1c',
//           borderRadius: 1,
//           maxHeight: 'calc(80% - 100px)',
//         }}
//       >
//         {chatHistory.map((message, index) => (
//           <Box key={index} sx={{ marginBottom: 1 }}>
//             <Paper
//               sx={{
//                 padding: 1,
//                 backgroundColor: message.type === 'user' ? '#3f3f3f' : '#444',
//                 maxWidth: '80%',
//                 marginLeft: message.type === 'user' ? 'auto' : 'initial',
//                 marginRight: message.type === 'bot' ? 'auto' : 'initial',
//                 color: 'white',
//               }}
//             >
//               <Typography variant="body1">{message.message}</Typography>
//             </Paper>
//           </Box>
//         ))}
//       </Box>

//       {/* Chat Input */}
//       <Grid container spacing={2}>
//         <Grid item xs={9}>
//           <TextField
//             fullWidth
//             variant="outlined"
//             placeholder="Ask your financial question..."
//             value={userQuery}
//             onChange={(e) => setUserQuery(e.target.value)}
//             sx={{ backgroundColor: '#444', color: 'white' }}
//           />
//         </Grid>
//         <Grid item xs={3}>
//           <Button
//             variant="contained"
//             color="primary"
//             sx={{ height: '100%' }}
//             onClick={handleUserQuery}
//           >
//             Ask
//           </Button>
//         </Grid>
//       </Grid>
//     </Box>
//   );
// };

// export default FinancialChatBot;

// import React, { useState } from 'react';
// import axios from 'axios';
// import { Box, Typography, TextField, Button, Paper, Grid, Divider } from '@mui/material';

// const FinancialChatBot = () => {
//   const [userQuery, setUserQuery] = useState('');
//   const [chatHistory, setChatHistory] = useState([]);  // To store the conversation

//   // Function to handle user question submission
//   const handleUserQuery = async () => {
//     if (userQuery.trim() === '') return;  // Don't submit empty queries
  
//     // Add user's query to the chat history
//     const newChatHistory = [...chatHistory, { type: 'user', message: userQuery }];
//     setChatHistory(newChatHistory);
//     setUserQuery('');  // Clear the input field
  
//     try {
//       // Send the query to the Flask backend (Financial QA API)
//       const response = await axios.get('http://127.0.0.1:5000/api/financial-qa', {
//         params: { query: userQuery },
//       });
  
//       console.log("Backend Response:", response.data);
  
//       if (response.data && response.data.symbol) {
//         const stockData = response.data;
//         const botResponse = `
//           Stock Symbol: ${stockData.symbol}\n
//           Price: ${stockData.price}\n
//           Change: ${stockData.change}\n
//           Change Percent: ${stockData.change_percent}\n
//           Previous Close: ${stockData.previous_close}
//         `;
        
//         setChatHistory([...newChatHistory, { type: 'bot', message: botResponse }]);
//       } else {
//         setChatHistory([...newChatHistory, { type: 'bot', message: 'No valid stock data found. Please try again.' }]);
//       }
//     } catch (error) {
//       console.error('Error fetching answer:', error);
//       setChatHistory([
//         ...newChatHistory,
//         { type: 'bot', message: 'Sorry, I couldn’t process that. Please try again.' }
//       ]);
//     }
//   };
  
//   return (
//     <Box
//       sx={{
//         width: '100%',
//         height: '80vh',
//         maxWidth: 600,
//         margin: '0 auto',
//         backgroundColor: '#2f2f2f',
//         color: 'white',
//         borderRadius: 2,
//         padding: 2,
//         display: 'flex',
//         flexDirection: 'column',
//       }}
//     >
//       {/* Chatbot Header */}
//       <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, textAlign: 'center' }}>
//         Financial Assistant Chatbot
//       </Typography>
//       <Divider sx={{ mb: 2 }} />

//       {/* Chat History */}
//       <Box
//         sx={{
//           flex: 1,
//           overflowY: 'auto',
//           marginBottom: 2,
//           padding: 1,
//           backgroundColor: '#1c1c1c',
//           borderRadius: 1,
//           maxHeight: 'calc(80% - 100px)',
//         }}
//       >
//         {chatHistory.map((message, index) => (
//           <Box key={index} sx={{ marginBottom: 1 }}>
//             <Paper
//               sx={{
//                 padding: 1,
//                 backgroundColor: message.type === 'user' ? '#3f3f3f' : '#444',
//                 maxWidth: '80%',
//                 marginLeft: message.type === 'user' ? 'auto' : 'initial',
//                 marginRight: message.type === 'bot' ? 'auto' : 'initial',
//                 color: 'white',
//               }}
//             >
//               <Typography variant="body1">{message.message}</Typography>
//             </Paper>
//           </Box>
//         ))}
//       </Box>

//       {/* Chat Input */}
//       <Grid container spacing={2}>
//         <Grid item xs={9}>
//           <TextField
//             fullWidth
//             variant="outlined"
//             placeholder="Ask your financial question..."
//             value={userQuery}
//             onChange={(e) => setUserQuery(e.target.value)}
//             sx={{ backgroundColor: '#444', color: 'white' }}
//           />
//         </Grid>
//         <Grid item xs={3}>
//           <Button
//             variant="contained"
//             color="primary"
//             sx={{ height: '100%' }}
//             onClick={handleUserQuery}
//           >
//             Ask
//           </Button>
//         </Grid>
//       </Grid>
//     </Box>
//   );
// };

// export default FinancialChatBot;



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
            <Typography>Analyzing...</Typography>
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