// BudgetClassification.js
import React from "react";
import { Treemap, ResponsiveContainer } from 'recharts';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#00C805', '#0088FE'];

const BudgetClassification = () => {
  // Sample data for budget categories
  const data = {
    name: 'Budget',
    children: [
      {
        name: 'Housing',
        value: 2500,
        children: [
          { name: 'Rent', value: 2000 },
          { name: 'Utilities', value: 300 },
          { name: 'Maintenance', value: 200 },
        ],
      },
      {
        name: 'Transportation',
        value: 800,
        children: [
          { name: 'Car Payment', value: 400 },
          { name: 'Gas', value: 200 },
          { name: 'Public Transit', value: 200 },
        ],
      },
      {
        name: 'Food',
        value: 600,
        children: [
          { name: 'Groceries', value: 400 },
          { name: 'Dining Out', value: 200 },
        ],
      },
      {
        name: 'Entertainment',
        value: 400,
        children: [
          { name: 'Streaming Services', value: 100 },
          { name: 'Hobbies', value: 200 },
          { name: 'Events', value: 100 },
        ],
      },
      {
        name: 'Savings',
        value: 1000,
        children: [
          { name: 'Emergency Fund', value: 500 },
          { name: 'Retirement', value: 300 },
          { name: 'Investments', value: 200 },
        ],
      },
      {
        name: 'Healthcare',
        value: 300,
        children: [
          { name: 'Insurance', value: 200 },
          { name: 'Medical Expenses', value: 100 },
        ],
      },
    ],
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <Treemap
          data={data.children}
          dataKey="value"
          ratio={4/3}
          stroke="#fff"
          fill="#8884d8"
          content={<CustomizedContent colors={COLORS} />}
        />
      </ResponsiveContainer>
    </div>
  );
};

const CustomizedContent = ({ root, depth, x, y, width, height, index, colors, name, value }) => {
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: depth < 2 ? colors[index % colors.length] : 'rgba(255,255,255,0)',
          stroke: '#fff',
          strokeWidth: 2 / (depth + 1e-10),
          strokeOpacity: 1 / (depth + 1e-10),
        }}
      />
      {depth === 1 ? (
        <text
          x={x + width / 2}
          y={y + height / 2 + 7}
          textAnchor="middle"
          fill="#fff"
          fontSize={14}
        >
          {name}
        </text>
      ) : null}
      {depth === 1 ? (
        <text
          x={x + 4}
          y={y + 18}
          fill="#fff"
          fontSize={16}
          fillOpacity={0.9}
        >
          {index + 1}
        </text>
      ) : null}
    </g>
  );
};

export default BudgetClassification;
