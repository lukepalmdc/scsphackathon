import React, { useState } from 'react';

function App() {
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

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
        setHistory([...newHistory, { role: "assistant", content: data.reply }]);
        setError(null);
      } else {
        setError(data.error || "Unknown error");
      }
    } catch (err) {
      setError("Failed to connect to backend.");
    }
  };

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
    </div>
  );
}

export default App;