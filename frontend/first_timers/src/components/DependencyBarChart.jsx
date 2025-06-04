import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function DependencyBarChart({ data }) {
  if (!data || data.length === 0) return null;

  const chartData = {
    labels: data.map(item => item.partner),
    datasets: [
      {
        label: "Dependency %",
        data: data.map(item => (item.dependency_pct ?? 0) * 100), // convert to percent
        backgroundColor: "#3498db"
      }
    ]
  };

  return <Bar data={chartData} options={{ responsive: true }} />;
}