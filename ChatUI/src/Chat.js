import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
// AUTH DISABLED - Commented out auth imports
// import { useAuth } from "./AuthContext";
// import { makeAuthenticatedRequest } from "./authService";
import "./App.css";

function randomThreadID() {
  return Math.random().toString(36).substring(2, 15);
}

function Chat() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! 😊 How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const threadID = useRef(randomThreadID());
  const messagesEndRef = useRef(null);
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  // AUTH DISABLED - Commented out auth hooks
  // const { token, logout } = useAuth();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // AUTH DISABLED - Using regular fetch instead of authenticated request
      const res = await fetch(backendUrl + "/invoke-graph", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMsg.text,
          threadID: threadID.current,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      let botMsg = "";
      setMessages((msgs) => [...msgs, { sender: "bot", text: "" }]);

      // Extract updater function outside the loop to avoid eslint warning
      const updateBotMessage = (text) => {
        setMessages((msgs) => {
          const updated = [...msgs];
          updated[updated.length - 1] = { sender: "bot", text };
          return updated;
        });
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        botMsg += new TextDecoder().decode(value);
        updateBotMessage(botMsg);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: "Error: Could not reach backend." },
      ]);
    }
    setLoading(false);
  };

  // AUTH DISABLED - Commented out logout handler
  // const handleLogout = () => {
  //   logout();
  // };

  return (
    <div className="chat-app">
      <div className="chat-header">
        <div className="header-content">
          {/* LOGO DISABLED - Commented out logo display
          <img 
            src="/assets/images/header-logo.png" 
            alt="Header Logo" 
            className="header-logo"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          */}
          {/* HEADING DISABLED - Commented out company name
          <span className="header-fallback">
            Meil|Megha Engineering And Infrastructure Ltd
          </span>
          */}
        </div>
        {/* AUTH DISABLED - Commented out logout button
        <button 
          className="logout-button" 
          onClick={handleLogout}
          title="Logout"
        >
          Logout
        </button>
        */}
      </div>
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.sender}`}>
            {msg.sender === "bot" ? (
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            ) : (
              msg.text
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-row" onSubmit={handleSend}>
        <textarea
          className="chat-input"
          placeholder="Ask Anything..."
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = e.target.scrollHeight + "px";
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (input.trim() && !loading) {
                handleSend(e);
                e.target.style.height = "auto";
              }
            }
          }}
          disabled={loading}
          rows={1}
        />
        <button
          className="chat-send"
          type="submit"
          disabled={loading || !input.trim()}
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default Chat;
