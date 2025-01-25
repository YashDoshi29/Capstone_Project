import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const DynamicGraphs = () => {
  const chartRef = useRef(null); // Chart instance
  const canvasRef = useRef(null); // Canvas element

  useEffect(() => {
    const ctx = canvasRef.current.getContext("2d");

    // Create the chart
    const chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: Array.from({ length: 10 }, (_, i) => `Point ${i + 1}`),
        datasets: [
          {
            label: "Expenses",
            data: Array(10).fill(0).map(() => Math.random() * 100),
            borderColor: "#FF6384",
            tension: 0.4,
          },
          {
            label: "Savings",
            data: Array(10).fill(0).map(() => Math.random() * 100),
            borderColor: "#36A2EB",
            tension: 0.4,
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

  return <canvas ref={canvasRef} id="dynamicLineGraph"></canvas>;
};

export default DynamicGraphs;
