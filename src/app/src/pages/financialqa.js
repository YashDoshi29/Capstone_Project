import React from "react";
import FinancialChatBot from "../components/financialqacomp"; // Import the chatbot component
import { Box, Typography, Container } from "@mui/material";

const FinancialQA = () => {
  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h3" sx={{ fontWeight: "bold", textAlign: "center", mb: 4 }}>
        Financial Assistant Chatbot
      </Typography>
      <FinancialChatBot />
    </Container>
  );
};

export default FinancialQA;
