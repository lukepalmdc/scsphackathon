import React, { useState, useEffect } from 'react';
import RadarRiskChart from "./components/RadarRiskChart";
import DependencyBarChart from "./components/DependencyBarChart";

function App() {
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [topRisks, setTopRisks] = useState([]);
  const [filteredRisks, setFilteredRisks] = useState([]);

  const fetchTopRiskCountries = async () => {
    try {
        const res = await fetch("http://localhost:8000/api/top-risk-countries");
        const data = await res.json();
        setTopRisks(data);
    } catch (err) {
        console.error("Error fetching risk countries:", err);
    }
};

  const handleSend = async () => {
  if (!prompt.trim()) return;

  const newHistory = [...history, { role: "user", content: prompt }];
  setHistory(newHistory);
  setPrompt("");

  try {
    const res = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const data = await res.json();

    if (res.ok) {
      const assistantMessage = { role: "assistant", content: data.reply };
      setHistory([...newHistory, assistantMessage]);
      setError(null);

      // === Attempt to extract {"compare": [...]} JSON block from GPT reply
      const match = data.reply.match(/{[^}]*"compare"[^}]*}/s);
      if (match) {
        try {
          const parsed = JSON.parse(match[0]);
          if (parsed.compare && Array.isArray(parsed.compare)) {
            const filtered = topRisks.filter(r =>
              parsed.compare.includes(r.partner)
            );
            setFilteredRisks(filtered); // Update your chart data
          }
        } catch (jsonErr) {
          console.warn("GPT returned invalid JSON compare block:", jsonErr);
        }
      }

    } else {
      setError(data.error || "Unknown error");
    }
  } catch (err) {
    setError("Failed to connect to backend.");
  }
};

  useEffect(() => {
  fetchTopRiskCountries();
}, []);

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>First Timers</h1>

      <div style={{ marginBottom: '1rem' }}>
        <textarea
          rows={4}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ width: '100%', padding: '0.5rem' }}
          placeholder="Ask me anything about supply chain risks, trade policy, or geopolitics..."
        />
        <button onClick={handleSend} style={{ marginTop: '0.5rem' }}>Send</button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px' }}>
        <h3>Chat History</h3>
        {history.map((msg, idx) => (
          <div key={idx} style={{ marginBottom: '1rem' }}>
            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
      </div>
      <div style={{ marginTop: '2rem' }}>
  <h2>📈 Supply Chain Dependency</h2>
  <DependencyBarChart data={filteredRisks.length > 0 ? filteredRisks : topRisks} />
</div>
      <div style={{ marginTop: '2rem' }}>
  <h2>🌍 Top 3 High-Risk Trade Partners</h2>
  <RadarRiskChart data={filteredRisks.length > 0 ? filteredRisks : topRisks} />
  <ul>
    {topRisks.map((item, idx) => (
      <li key={idx}>
        <strong>{item.partner}</strong>: Risk Score = {item.risk_score.toFixed(2)}
      </li>
    ))}
  </ul>
</div>
    </div>
  );
}

export default App;