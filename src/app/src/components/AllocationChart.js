import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const AllocationChart = () => {
  const data = {
    labels: ['Housing', 'Transportation', 'Food', 'Utilities', 'Savings', 'Entertainment'],
    datasets: [
      {
        data: [30, 15, 20, 10, 15, 10],
        backgroundColor: [
          '#00C805',  // Green
          '#FF4B4B',  // Red
          '#36A2EB',  // Blue
          '#FFCD56',  // Yellow
          '#9966FF',  // Purple
          '#FF9F40',  // Orange
        ],
        borderColor: 'rgba(0, 0, 0, 0)',
        borderWidth: 2,
        hoverOffset: 15,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: '#b0b0b0',
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 12,
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed}%`;
          }
        }
      }
    },
    animation: {
      animateRotate: true,
      animateScale: true
    }
  };

  return (
    <div style={{ height: '400px', width: '100%', position: 'relative' }}>
      <Doughnut data={data} options={options} />
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          pointerEvents: 'none'
        }}
      >
        <div style={{ color: '#b0b0b0', fontSize: '14px' }}>Total Budget</div>
        <div style={{ color: '#fff', fontSize: '24px', fontWeight: 'bold' }}>$5,000</div>
      </div>
    </div>
  );
};

export default AllocationChart; 