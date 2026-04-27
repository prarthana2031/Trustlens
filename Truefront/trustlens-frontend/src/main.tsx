import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';

console.log("App starting..."); // Debug log

try {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  console.log("App rendered successfully");
} catch (error) {
  console.error("Failed to render app:", error);
  document.getElementById('root')!.innerHTML = `<pre>Error: ${error}</pre>`;
}
