import { useState, useEffect } from "react";

const PingComponent = () => {
  const [response, setResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  

  useEffect(() => {
    const API_URL = import.meta.env.VITE_REACT_APP_API_URL || "http://localhost:5000/ping";
    const fetchPing = async () => {
      try {
        console.log(API_URL)
        const res = await fetch(API_URL + 'ping');
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        const data = await res.text(); // If API returns plain text
        setResponse(data);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    fetchPing();
  }, []);

  return (
    <div className="p-4 border rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-2">Ping API Response</h2>
      {error ? (
        <p className="text-red-500">Error: {error}</p>
      ) : (
        <p className="text-green-500">Response: {response}</p>
      )}
    </div>
  );
};

export default PingComponent;