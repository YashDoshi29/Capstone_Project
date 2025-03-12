import React, { useState, useEffect } from "react";

const FinancialNews = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    console.log("Financial News Component has mounted.");
  }, []);

  const sendQueryToChatbot = async (query) => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:5000/chatbot", {  // Backend URL (Flask app)
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (response.ok) {
        const botResponse = data.answer || "Sorry, I couldn't find any relevant news.";
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: "user", text: query },
          { sender: "bot", text: botResponse },
        ]);
      } else {
        setError("Failed to get response from the chatbot.");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("An error occurred while fetching the data.");
    } finally {
      setLoading(false);
    }
  };

  const handleUserInputChange = (event) => {
    setUserInput(event.target.value);
  };

  const handleSendMessage = (event) => {
    event.preventDefault();
    if (userInput.trim()) {
      sendQueryToChatbot(userInput);
      setUserInput(""); // Reset the input field
    }
  };

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h2>Financial News Chatbot</h2>

      <div style={{ marginBottom: "20px", maxHeight: "400px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
            <strong>{msg.sender === "user" ? "You" : "Bot"}:</strong>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={handleSendMessage} style={{ display: "flex", justifyContent: "center", marginTop: "10px" }}>
        <input
          type="text"
          value={userInput}
          onChange={handleUserInputChange}
          placeholder="Ask a question..."
          style={{ padding: "10px", width: "300px" }}
        />
        <button type="submit" disabled={loading} style={{ padding: "10px 20px", marginLeft: "10px" }}>
          {loading ? "Loading..." : "Send"}
        </button>
      </form>
    </div>
  );
};

// const FinancialNews = () => {
//   return (
//     <div style={{ textAlign: "center", padding: "20px" }}>
//       <FinancialNews />
//     </div>
//   );
// };

export default FinancialNews;
