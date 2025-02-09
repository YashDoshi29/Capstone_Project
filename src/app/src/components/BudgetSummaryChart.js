// BudgetSummaryChart.js
import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const BudgetSummaryChart = () => {
  // Sample chart data; replace with dynamic data as needed
  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [
      {
        label: "Expenses",
        data: [1200, 1500, 1000, 1800, 1300, 1600],
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 1,
      },
      {
        label: "Budget",
        data: [1500, 1500, 1500, 1500, 1500, 1500],
        backgroundColor: "rgba(255, 99, 132, 0.6)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
    ],
  };

  // Chart configuration options
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "white", // White text for legend labels
        },
      },
      title: {
        display: true,
        text: "Monthly Budget vs Expenses",
        color: "white", // White title text
      },
    },
    scales: {
      x: {
        ticks: {
          color: "white", // White text on the x-axis
        },
        grid: {
          color: "rgba(255, 255, 255, 0.2)", // Light grid lines for x-axis
        },
      },
      y: {
        ticks: {
          color: "white", // White text on the y-axis
        },
        grid: {
          color: "rgba(255, 255, 255, 0.2)", // Light grid lines for y-axis
        },
      },
    },
  };

  return <Bar data={data} options={options} />;
};

export default BudgetSummaryChart;
