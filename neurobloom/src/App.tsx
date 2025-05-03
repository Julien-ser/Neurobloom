import { useState, useRef, useEffect } from 'react';
import Webcam from "react-webcam";

export default function App() {
  // States
  const [emotion, setEmotion] = useState("Neutral");
  const [suggestedAction, setSuggestedAction] = useState("");
  const [journalContent, setJournalContent] = useState("");
  const [agentResponse, setAgentResponse] = useState("");
  const [journalQuery, setJournalQuery] = useState("");
  const [taskQuery, setTaskQuery] = useState("");
  const webcamRef = useRef(null);
  const sessionId = "user_123"; // You can replace this with a dynamic session ID if needed

  // Emotion Detection
  const handleDetectEmotion = async () => {
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        setEmotion("Error");
        setSuggestedAction("Try again");
        setAgentResponse("Could not capture image");
        return;
      }

      const blob = await (await fetch(imageSrc)).blob();
      const formData = new FormData();
      formData.append("image", blob, "webcam.jpg");
      formData.append("sessionId", sessionId);

      const response = await fetch("http://localhost:8000/emotion/upload", {
        method: "POST",
        body: formData
      });

      const result = await response.json();
      console.log(result);
      if (result.error) {
        setEmotion("Error");
        setSuggestedAction("Try again");
        setAgentResponse(`Error: ${result.error}`);
        return;
      }

      console.log(result.emotion.response.data.emotion);
      // Properly set emotion and suggested action based on response
      const detectedEmotion = result.emotion.response.data.emotion || "unknown"; // Ensure "emotion" field exists in response
      const suggestedAction = result.emotion.response.data.suggested_action || "Stay focused";
      const journalContent = result.emotion.response.data.journal_content || "No content available";
      console.log(detectedEmotion);
      setEmotion(detectedEmotion);
      setSuggestedAction(suggestedAction);
      setJournalContent(journalContent);

      // Automatically trigger the journal query with the journalContent
      handleJournalQuery(journalContent);

    } catch (error) {
      console.error("Emotion detection failed:", error);
      setEmotion("Error");
      setSuggestedAction("Try again");
      setAgentResponse(`Error: ${error.message}`);
    }
  };

  // Handle Journal Query
  const handleJournalQuery = async (query) => {
    try {
      const response = await fetch("http://localhost:8000/agent/journal", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: query, sessionId })
      });

      const result = await response.json();
      console.log(result);
      const journalQuery = result.response.content || "No response from journal agent.";
      setAgentResponse(journalQuery);
      console.log(journalQuery);
    } catch (error) {
      console.error("Journal query failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };
  // Handle Task Query
  const handleTaskQuery = async () => {
    try {
      const response = await fetch("http://localhost:8000/agent/task", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: taskQuery, sessionId })
      });

      const result = await response.json();
      setAgentResponse(result.response || "No response from task agent.");
    } catch (error) {
      console.error("Task query failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };

  // Call handleDetectEmotion when the component is mounted (optional)
  useEffect(() => {
    console.log("Simulating emotion detection...");
    handleDetectEmotion();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 p-4 text-gray-800">
      <h1 className="text-3xl font-bold text-center mb-6">Neurobloom 🌸</h1>

      {/* Webcam + Emotion */}
      <div className="flex flex-col items-center gap-4 mb-8">
        <Webcam
          ref={webcamRef}
          className="rounded-lg shadow-md w-64 h-48"
          screenshotFormat="image/jpeg"
        />
        <button
          onClick={handleDetectEmotion}
          className="px-4 py-2 bg-indigo-600 text-white rounded-xl shadow"
        >
          Analyze Emotion
        </button>
        <div className="text-xl">Detected Emotion: <span className="font-semibold">{emotion}</span></div>
        <div className="italic text-sm text-gray-600">
          Suggested Action: {suggestedAction}
        </div>
        <div className="italic text-sm text-gray-600 mt-2">
          Journal Content: {journalContent}
        </div>
      </div>

      {/* Journal Input and Response */}
      <div className="mb-8">
        <textarea
          value={journalQuery} // This will hold the user input or agent's response
          onChange={(e) => setJournalQuery(e.target.value)} // Update the journal query state
          placeholder="Write something for your journal..."
          className="w-full p-4 border border-gray-300 rounded-lg shadow-md mb-2"
        />
        <button
          onClick={() => handleJournalQuery(journalQuery)} // Pass the current journalQuery to the handler
          className="px-4 py-2 bg-green-600 text-white rounded-xl shadow"
        >
          Submit Journal
        </button>

        {/* Optionally, show a message after the response */}
        {agentResponse && (
          <div className="mt-4 p-3 bg-white rounded-lg shadow">
            <h3 className="font-bold mb-1">System Response:</h3>
            <p className="text-gray-700">{agentResponse}</p>
          </div>
        )}
      </div>


      {/* Task Input */}
      {/* Task Input and Response */}
      <div className="mb-8">
        <textarea
          value={taskQuery}
          onChange={(e) => setTaskQuery(e.target.value)}
          placeholder="What's your task?"
          className="w-full p-4 border border-gray-300 rounded-lg shadow-md mb-2"
        />
        <button
          onClick={handleTaskQuery}
          className="px-4 py-2 bg-blue-600 text-white rounded-xl shadow"
        >
          Submit Task
        </button>
      </div>

      {/* Display agent responses */}
      {agentResponse && (
        <div className="mt-4 p-3 bg-white rounded-lg shadow">
          <h3 className="font-bold mb-1">System Response:</h3>
          <p className="text-gray-700">{agentResponse}</p>
        </div>
      )}
    </div>
  );
}
