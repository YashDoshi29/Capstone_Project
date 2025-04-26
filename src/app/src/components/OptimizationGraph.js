import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const OptimizationGraph = () => {
  const data = {
    labels: ['Housing', 'Transportation', 'Food', 'Utilities', 'Entertainment'],
    datasets: [
      {
        label: 'Current Spending',
        data: [1500, 750, 1000, 500, 500],
        backgroundColor: 'rgba(255, 75, 75, 0.7)',
        borderColor: 'rgba(255, 75, 75, 1)',
        borderWidth: 1,
      },
      {
        label: 'Optimized Budget',
        data: [1300, 600, 800, 450, 400],
        backgroundColor: 'rgba(0, 200, 5, 0.7)',
        borderColor: 'rgba(0, 200, 5, 1)',
        borderWidth: 1,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#b0b0b0',
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
        }
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: $${context.parsed.y}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          color: '#b0b0b0',
        }
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          drawBorder: false,
        },
        ticks: {
          color: '#b0b0b0',
          callback: function(value) {
            return '$' + value;
          }
        }
      }
    },
    barPercentage: 0.7,
    categoryPercentage: 0.8,
  };

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default OptimizationGraph; 