import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import styled from "styled-components";

interface SupplierPerformanceData {
  name: string;
  orders: number;
  revenue: number;
  rating: number;
}

interface SupplierPerformanceChartProps {
  data: SupplierPerformanceData[];
  height?: number;
}

const SupplierPerformanceChart: React.FC<SupplierPerformanceChartProps> = ({
  data,
  height = 300,
}) => {
  return (
    <ChartContainer>
      <ChartTitle>Supplier Performance</ChartTitle>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip
            formatter={(value: number, name: string) => {
              if (name === "revenue")
                return [`$${value.toLocaleString()}`, "Revenue"];
              if (name === "rating") return [`${value}/5`, "Rating"];
              return [value, name];
            }}
          />
          <Legend />
          <Bar yAxisId="left" dataKey="orders" fill="#3498db" name="Orders" />
          <Bar
            yAxisId="left"
            dataKey="revenue"
            fill="#2ecc71"
            name="Revenue ($)"
          />
          <Bar
            yAxisId="right"
            dataKey="rating"
            fill="#f39c12"
            name="Rating (1-5)"
          />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

const ChartContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const ChartTitle = styled.h3`
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
`;

export default SupplierPerformanceChart;
