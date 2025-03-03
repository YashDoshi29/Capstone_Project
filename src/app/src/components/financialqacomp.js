import React, { useState } from 'react';
import axios from 'axios';
import { Box, Typography, TextField, Button, Paper, Grid, Divider } from '@mui/material';

const FinancialChatBot = () => {
  const [userQuery, setUserQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);  // To store the conversation

  // Function to handle user question submission
  const handleUserQuery = async () => {
    if (userQuery.trim() === '') return;  // Don't submit empty queries

    // Add user's query to the chat history
    const newChatHistory = [...chatHistory, { type: 'user', message: userQuery }];
    setChatHistory(newChatHistory);
    setUserQuery('');  // Clear the input field

    try {
      // Send the query to the Flask backend (Financial QA API)
      const response = await axios.get('http://localhost:5000/api/financial-qa', {
        params: { query: userQuery },
      });

      // Add the response from the Financial QA agent to the chat history
      const botResponse = response.data.answer;
      setChatHistory([...newChatHistory, { type: 'bot', message: botResponse }]);
    } catch (error) {
      console.error('Error fetching answer:', error);
      setChatHistory([
        ...newChatHistory,
        { type: 'bot', message: 'Sorry, I couldn’t process that. Please try again.' }
      ]);
    }
  };

  return (
    <Box
      sx={{
        width: '100%',
        height: '80vh',
        maxWidth: 600,
        margin: '0 auto',
        backgroundColor: '#2f2f2f',
        color: 'white',
        borderRadius: 2,
        padding: 2,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Chatbot Header */}
      <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, textAlign: 'center' }}>
        Financial Assistant Chatbot
      </Typography>
      <Divider sx={{ mb: 2 }} />

      {/* Chat History */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          marginBottom: 2,
          padding: 1,
          backgroundColor: '#1c1c1c',
          borderRadius: 1,
          maxHeight: 'calc(80% - 100px)',
        }}
      >
        {chatHistory.map((message, index) => (
          <Box key={index} sx={{ marginBottom: 1 }}>
            <Paper
              sx={{
                padding: 1,
                backgroundColor: message.type === 'user' ? '#3f3f3f' : '#444',
                maxWidth: '80%',
                marginLeft: message.type === 'user' ? 'auto' : 'initial',
                marginRight: message.type === 'bot' ? 'auto' : 'initial',
                color: 'white',
              }}
            >
              <Typography variant="body1">{message.message}</Typography>
            </Paper>
          </Box>
        ))}
      </Box>

      {/* Chat Input */}
      <Grid container spacing={2}>
        <Grid item xs={9}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask your financial question..."
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            sx={{ backgroundColor: '#444', color: 'white' }}
          />
        </Grid>
        <Grid item xs={3}>
          <Button
            variant="contained"
            color="primary"
            sx={{ height: '100%' }}
            onClick={handleUserQuery}
          >
            Ask
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FinancialChatBot;
