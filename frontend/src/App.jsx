import { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');

  const askQuestion = async () => {
    const res = await fetch('http://127.0.0.1:8000/api/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    setResponse(data.answer);
  };

  return (
    <div className="App">
      <h1>TDS Virtual TA</h1>
      <textarea
        rows={4}
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Ask me anything from the course..."
      />
      <button onClick={askQuestion}>Ask</button>
      <div className="response">{response}</div>
    </div>
  );
}

export default App;
