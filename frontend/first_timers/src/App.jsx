import React, { useState } from "react";
import { getTradeData, getRiskScore, getBrief } from "./api";

function App() {
    const [hsCode, setHsCode] = useState("1006");
    const [year, setYear] = useState(2023);
    const [table, setTable] = useState([]);
    const [brief, setBrief] = useState("");
    const [score, setScore] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try{
            const [data, risk, summary] = await Promise.all([
                getTradeData(hsCode, year),
                getRiskScore(hsCode, year),
                getBrief(hsCode, year),
            ]);
            setTable(data);
            setScore(risk.risk_score);
            setBrief(summary.brief);
        } catch (err) {
            setError("Failed to fetch data");
        }
        setLoading(false);
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold">First Timers Landing Page</h1>
            <input value={hsCode} onChange={(e) => setHsCode(e.target.value)} />
            <input type="number" value={year} onChange={(e) => setYear(+e.target.value)} />
            <button onClick={fetchData} disabled={loading}>Run</button>

            {loading && <p>Loading...</p>}
            {error && <p style={{ color:"red" }}>{error}</p>}
            {score && <h2>Risk Score: {score}</h2>}
            {brief && <p>{brief}</p>}
            <table>
                <thead>
                    <tr><th>Partner</th><th>USD</th><th>%</th></tr>
                </thead>
                <tbody>
                    {table.map((row, i) => (
                        <tr key={i}>
                            <td>{row.partner}</td>
                            <td>{row.trade_value_usd}</td>
                            <td>{row.percent_of_total.toFixed(1)}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default App;