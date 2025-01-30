import React from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";

const TransactionTable = () => {
  const transactions = [
    { date: "2025-01-01", description: "Walmart", amount: 55.2, category: "Groceries" },
    { date: "2025-01-02", description: "Netflix", amount: 15.99, category: "Entertainment" },
    { date: "2025-01-03", description: "Uber", amount: 23.0, category: "Transport" },
  ];

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Amount ($)</TableCell>
            <TableCell>Category</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {transactions.map((txn, index) => (
            <TableRow key={index}>
              <TableCell>{txn.date}</TableCell>
              <TableCell>{txn.description}</TableCell>
              <TableCell>{txn.amount}</TableCell>
              <TableCell>{txn.category}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TransactionTable;
