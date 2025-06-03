import React, { useState } from "react";
import { getTradeData, getRiskScore, getBrief } from "./api";
// TODO: change api imports to reflect actual terms, delete comment later 

function App() {
    const [hsCode, setHsCode] = useState("1006");
    const [year, setYear] = useState(2023);
    const [table, setTable] = useState([]); // Stores trade data table as an array
    const [brief, setBrief] = useState("");
    const [score, setScore] = useState(null);
    const [loading, setLoading] = useState(false); // Displayed when data is being fetched
    const [error, setError] = useState(null); // Error message
    const [chatInput, setChatInput] = useState("");
    const [chatHistory, setChatHistory] = useState([]);
    const [chatFile, setChatFile] = useState(null);

    const fetchData = async () => {
        setLoading(true); // Set loading to true
        setError(null); // Clear errors
        try{
            const [data, risk, summary] = await Promise.all([ // Calls all API functions in parallel, better performance
                getTradeData(hsCode, year),
                getRiskScore(hsCode, year),
                getBrief(hsCode, year),
            ]);
            setTable(data); // Updates with fetched data
            setScore(risk.risk_score); // Updates with fetched data
            setBrief(summary.brief); // Updates with fetched data
        } catch (err) { // Error handling
            setError("Failed to fetch data");
        }
        setLoading(false);
    };

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatInput && !chatFile) return;
        setChatHistory((prev) => [...prev, { sender: "user", text: chatInput, file: chatFile?.name }]);
        
        const formData = new FormData();
        formData.append("message", chatInput);
        if (chatFile) formData.append("file", chatFile);

        try {
            const res = await fetch("http://localhost:8000/api/chat", {
                method: "POST",
                body: formData,
            });
            const data = await res.json();
            setChatHistory((prev) => [...prev, { sender: "bot", text:data.reply }]);
        } catch (err) {
            setChatHistory((prev) => [...prev, { sender: "bot", text: "Error: Could not get response."}]);
        }
        setChatInput("");
        setChatFile(null);
    }

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
                    {table.map((row, i) => ( // Renders table of trade data, mapping each row
                        <tr key={i}>
                            <td>{row.partner}</td>
                            <td>{row.trade_value_usd}</td>
                            <td>{row.percent_of_total.toFixed(1)}%</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <hr style={{ margin: "2em 0" }} />
            <h2>Chatbot</h2>
            <div style={{ border: "1px solid #ccc", padding: "1em", maxHeight: 300, overflowY: "auto" }}>
                {chatHistory.map((msg, i) => (
                    <div key={i} style={{ margin: "0.5em 0" }}>
                        <b>{msg.sender === "user" ? "You" : "Bot"}:</b> {msg.text}
                        {msg.file && <span> <i>(attached: {msg.file})</i></span>}
                    </div>
                ))}
                <form onSubmit={handleChatSubmit} style={{ marginTop: "1em" }}>
                    <input 
                        type="text"
                        value={chatInput}
                        onChange={e => setChatInput(e.target.value)}
                        placeholder="Type your prompt..."
                        style={{ width: "60%" }}
                    />
                    <input
                        type="file"
                        accept=".txt,.pdf,.jpeg,.png,.jpg"
                        onChange={e => setChatFile(e.target.files[0])}
                        style={{ marginLeft: "1em" }}
                    />
                    <button type="submit"style={{ marginLeft: "1em" }}>Submit</button>
                </form>
            </div>
        </div>
    );
}

export default App;