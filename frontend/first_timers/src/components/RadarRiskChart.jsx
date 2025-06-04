// frontend/src/components/RadarRiskChart.jsx

import React from "react";
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

export default function RadarRiskChart({ data }) {
  if (!data || data.length === 0) return null;

  const chartData = {
    labels: data.map(item => item.partner),
    datasets: [
      {
        label: "Risk Score",
        data: data.map(item => item.risk_score),
        backgroundColor: "rgba(231, 76, 60, 0.2)",
        borderColor: "#e74c3c",
        pointBackgroundColor: "#e74c3c",
        fill: true,
      }
    ]
  };

  const options = {
    scales: {
      r: {
        beginAtZero: true,
        max: Math.max(...data.map(d => d.risk_score)) * 1.2,
        ticks: {
          stepSize: 10
        }
      }
    }
  };

  return <Radar data={chartData} options={options} />;
}