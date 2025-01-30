import React from "react";
import { Grid2, Paper, Typography, Box } from "@mui/material";
import TransactionTable from "../components/TransactionTable";
import PieChart from "../components/PieChart";

const DashboardPage = () => {
  return (
    <Box sx={{ padding: "2rem", backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
      <Typography variant="h4" gutterBottom>
        Financial Dashboard
      </Typography>

      <Grid2 container spacing={4}>
        {/* Expense Chart */}
        <Grid2 item xs={12} md={6}>
          <Paper sx={{ padding: "1rem", height: "100%" }}>
            <Typography variant="h6">Expense Breakdown</Typography>
            <PieChart />
          </Paper>
        </Grid2>

        {/* Budget Summary */}
        <Grid2 item xs={12} md={6}>
          <Paper sx={{ padding: "1rem", height: "100%" }}>
            <Typography variant="h6">Budget Optimization</Typography>
            <Typography variant="body1" sx={{ marginTop: "1rem" }}>
              Your spending is 20% higher than last month. Consider reducing your dining expenses by $150 to save more.
            </Typography>
          </Paper>
        </Grid2>

        {/* Transaction Table */}
        <Grid2 item xs={12}>
          <Paper sx={{ padding: "1rem" }}>
            <Typography variant="h6">Recent Transactions</Typography>
            <TransactionTable />
          </Paper>
        </Grid2>
      </Grid2>
    </Box>
  );
};

export default DashboardPage;
