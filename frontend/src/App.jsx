import { useState } from "react";
import { createChatSession, sendMessage } from "./api";
import "./App.css";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    if (!input.trim()) return;

    const userText = input;
    setInput("");
    setLoading(true);

    try {
      let currentSessionId = sessionId;

      if (!currentSessionId) {
        const session = await createChatSession("New Chat");
        currentSessionId = session.id;
        setSessionId(session.id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content: userText,
        },
      ]);

      const response = await sendMessage(currentSessionId, userText);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.ai_message.content,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please check backend server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      handleSend();
    }
  }

  return (
    <div className="app">
      <div className="chat-container">
        <h1>AI Dashboard Chat</h1>
        <p className="subtitle">Ask normal questions or distance questions.</p>

        <div className="messages-box">
          {messages.length === 0 && (
            <div className="empty-message">
              Start by typing a message below.
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.role === "user"
                  ? "message user-message"
                  : "message ai-message"
              }
            >
              <strong>{message.role === "user" ? "You" : "AI"}</strong>
              <p>{message.content}</p>
            </div>
          ))}

          {loading && <div className="loading">AI is thinking...</div>}
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button onClick={handleSend} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;