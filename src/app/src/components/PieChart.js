import React from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";

// Register the required components for the chart
ChartJS.register(ArcElement, Tooltip, Legend);

const PieChart = () => {
  const data = {
    labels: ["Groceries", "Rent", "Utilities", "Entertainment"],
    datasets: [
      {
        label: "Expenses",
        data: [300, 1000, 200, 150], // Example data
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
        hoverOffset: 4,
      },
    ],
  };

  return <Pie data={data} />;
};

export default PieChart;

