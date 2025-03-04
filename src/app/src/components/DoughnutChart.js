import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const DoughnutChart = () => {
  const chartRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const ctx = canvasRef.current.getContext("2d");

    const chartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Stocks", "Real Estate", "Crypto", "Savings", "Mutual Funds"],
        datasets: [
          {
            label: "Investment.js Distribution",
            data: [40, 25, 15, 10, 10],
            backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
          },
        ],
      },
    });

    chartRef.current = chartInstance;

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);

  return <canvas ref={canvasRef} id="doughnutChart"></canvas>;
};

export default DoughnutChart;
