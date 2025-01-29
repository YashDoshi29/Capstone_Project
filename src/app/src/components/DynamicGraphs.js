import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const DynamicGraphs = () => {
  const chartRef = useRef(null);   // Holds the Chart.js instance
  const canvasRef = useRef(null);  // Reference to the canvas element

  useEffect(() => {
    // 1) A dummy “realistic” monthly budget dataset
    //    You can replace with real data from an API if needed
    const budgetData = [
      { month: "Jan", expenses: 500,  savings: 200 },
      { month: "Feb", expenses: 600,  savings: 250 },
      { month: "Mar", expenses: 450,  savings: 300 },
      { month: "Apr", expenses: 550,  savings: 350 },
      { month: "May", expenses: 650,  savings: 320 },
      { month: "Jun", expenses: 700,  savings: 400 },
      { month: "Jul", expenses: 750,  savings: 450 },
      { month: "Aug", expenses: 680,  savings: 420 },
      { month: "Sep", expenses: 620,  savings: 380 },
      { month: "Oct", expenses: 720,  savings: 480 },
      { month: "Nov", expenses: 680,  savings: 420 },
      { month: "Dec", expenses: 800,  savings: 500 },
    ];

    // 2) Initialize the chart with empty data
    const ctx = canvasRef.current.getContext("2d");
    const chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: [], // We'll fill these dynamically
        datasets: [
          {
            label: "Expenses",
            data: [],
            borderColor: "#FF6384",
            tension: 0.4,
          },
          {
            label: "Savings",
            data: [],
            borderColor: "#36A2EB",
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        animation: {
          duration: 500, // Each new point animates over 0.5s
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
    chartRef.current = chartInstance;

    // 3) Add data points one at a time, on an interval
    let index = 0;
    const intervalId = setInterval(() => {
      // If we've added all points, stop
      if (index >= budgetData.length) {
        clearInterval(intervalId);
        return;
      }

      const { month, expenses, savings } = budgetData[index];
      chartInstance.data.labels.push(month);
      chartInstance.data.datasets[0].data.push(expenses);
      chartInstance.data.datasets[1].data.push(savings);

      // Redraw chart
      chartInstance.update();
      index++;
    }, 1000); // 1 second per new data point

    // 4) Cleanup on unmount
    return () => {
      clearInterval(intervalId);
      chartInstance.destroy();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      id="dynamicLineGraph"
    />
  );
};

export default DynamicGraphs;
