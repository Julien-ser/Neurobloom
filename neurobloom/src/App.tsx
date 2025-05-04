import { useState, useRef, useEffect } from 'react';
import Webcam from "react-webcam";

export default function App() {
  const [emotion, setEmotion] = useState("Neutral");
  const [suggestedAction, setSuggestedAction] = useState("");
  const [journalContent, setJournalContent] = useState("");
  const [agentResponse, setAgentResponse] = useState("");
  const [journalQuery, setJournalQuery] = useState("");
  const [taskQuery, setTaskQuery] = useState("");
  const [journalEntries, setJournalEntries] = useState([]);
  const [taskList, setTaskList] = useState([]);
  const webcamRef = useRef(null);
  const sessionId = "user_123";

  const handleDetectEmotion = async () => {
    try {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        setEmotion("Face not found");
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
      if (result.error) {
        setEmotion("Face not found");
        setSuggestedAction("Try again");
        setAgentResponse(`Error: ${result.error}`);
        return;
      }

      const detectedEmotion = result.emotion.response.data.emotion || "unknown"; 
      const suggestedAction = result.emotion.response.data.suggested_action || "Stay focused";
      const journalContent = result.emotion.response.data.journal_content || "No content available";
      setEmotion(detectedEmotion);
      setSuggestedAction(suggestedAction);
      setTaskQuery(suggestedAction);
      setJournalContent(journalContent);
      setJournalQuery(journalContent);

      await augmentJournalWithAI(journalContent);
      await handleTaskQueryDirect(suggestedAction);
    } catch (error) {
      console.error("Emotion detection failed:", error);
      setEmotion("Face not found");
      setSuggestedAction("Try again");
      setAgentResponse(`Face not found: ${error.message}`);
    }
  };

  const handleJournalQuery = async (query) => {
    try {
      const response = await fetch("http://localhost:8000/agent/journal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, sessionId })
      });

      const result = await response.json();
      const journalResponse = result.response.content || "No response from journal agent.";
      setJournalEntries(prev => [...prev, { input: query, response: journalResponse }]);
      setJournalQuery("");
    } catch (error) {
      console.error("Journal query failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };

  const handleSimpleJournalSubmit = () => {
    handleTaskQueryDirect("life note file entry");
    if (!journalQuery.trim()) return;
    setJournalEntries(prev => [...prev, { input: journalQuery, response: "" }]);
    setJournalQuery("");
  };

  const augmentJournalWithAI = async (query) => {
    try {
      const response = await fetch("http://localhost:8000/agent/journal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, sessionId })
      });
  
      const result = await response.json();
      const journalResponse = result.response.content || "No response from journal agent.";
      setJournalQuery(prev => `${prev}\n\n${journalResponse}`);
    } catch (error) {
      console.error("AI augment failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };
  

  const handleTaskQueryDirect = async (query) => {
    try {
      const response = await fetch("http://localhost:8000/agent/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, sessionId })
      });
  
      const result = await response.json();
      setAgentResponse(result.response || "No response from task agent.");
      const newTask = {
        id: Date.now(),
        query,
        response: result.response || "No response",
        isCompleted: false
      };
  
      setTaskList(prev => [...prev, newTask]);
    } catch (error) {
      console.error("Task query failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };
  
  const handleTaskQuery = async () => {
    try {
      const response = await fetch("http://localhost:8000/agent/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: taskQuery, sessionId })
      });

      const result = await response.json();
      setAgentResponse(result.response || "No response from task agent.");
      const newTask = {
        id: Date.now(),
        query: taskQuery,
        response: result.response || "No response",
        isCompleted: false
      };

      setTaskList(prev => [...prev, newTask]);
      setTaskQuery("");
    } catch (error) {
      console.error("Task query failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };

  const completeTask = (taskId) => {
    const task = taskList.find(task => task.id === taskId);
    if (!task) return;
    setTaskList(prevTasks => prevTasks.filter(task => task.id !== taskId));
    setJournalQuery(prev => `${prev}\n\nTask complete: ${task.query}`);
    setAgentResponse(`Task "${task.query}" marked as complete.`);
  };

  useEffect(() => {
    console.log("Simulating emotion detection...");
    handleDetectEmotion();
  }, []);

  const buttonClass = "transition-transform transform hover:scale-105 px-4 py-2 rounded-xl shadow text-white font-semibold";
  const sectionCard = "bg-white bg-opacity-80 backdrop-blur-lg p-4 rounded-xl shadow-xl";

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-200 via-purple-100 to-blue-200 p-6 text-gray-800 font-sans">
      <h1 className="text-4xl font-extrabold text-center mb-10 tracking-tight text-indigo-800 drop-shadow-lg">Neurobloom 🌸</h1>

      {/* Emotion & Webcam */}
      <div className={`${sectionCard} mb-8`}>
        <h2 className="text-2xl font-bold mb-4">Emotion Detection</h2>
        <div className="flex flex-col md:flex-row items-center gap-6">
          <Webcam ref={webcamRef} className="rounded-lg shadow-md w-64 h-48 border-2 border-indigo-400" screenshotFormat="image/jpeg" />
          <div className="flex flex-col gap-3 w-full max-w-md">
            <button onClick={handleDetectEmotion} className={`${buttonClass} bg-indigo-600 hover:bg-indigo-700`}>
              Analyze Emotion
            </button>
            <p className="text-lg">Detected Emotion: <span className="font-semibold">{emotion}</span></p>
            <p className="text-sm italic text-gray-600">Suggested Action: {suggestedAction}</p>
            <p className="text-sm italic text-gray-600">Journal Content: {journalContent}</p>
          </div>
        </div>
      </div>

      {/* Journal Section */}
      <div className={`${sectionCard} mb-8`}>
        <h2 className="text-2xl font-bold mb-4">Journal</h2>
        <textarea
          value={journalQuery}
          onChange={(e) => setJournalQuery(e.target.value)}
          placeholder="Write something for your journal..."
          className="w-full p-4 border border-gray-300 rounded-lg shadow mb-4"
        />
        <div className="flex gap-4 mb-4">
          <button onClick={handleSimpleJournalSubmit} className={`${buttonClass} bg-green-600 hover:bg-green-700`}>
            Submit Journal
          </button>
          <button
            onClick={async () => {
              try {
                const response = await fetch("http://localhost:8000/agent/journal", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ query: journalQuery, sessionId })
                });

                const result = await response.json();
                const journalResponse = result.response.content || "No response from journal agent.";
                setJournalQuery(prev => `${prev}\n\n${journalResponse}`);
              } catch (error) {
                console.error("AI augment failed:", error);
                setAgentResponse(`Error: ${error.message}`);
              }
            }}
            className={`${buttonClass} bg-purple-600 hover:bg-purple-700`}
          >
            AI Add to Journal
          </button>
        </div>
        {journalEntries.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Journal History</h3>
            {journalEntries.map((entry, idx) => (
              <div key={idx} className="bg-white p-3 rounded-lg shadow text-gray-700">
                <p className="font-semibold">You:</p>
                <p>{entry.input}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Task Section */}
      <div className={`${sectionCard}`}>
        <h2 className="text-2xl font-bold mb-4">Tasks</h2>
        <textarea
          value={taskQuery}
          onChange={(e) => setTaskQuery(e.target.value)}
          placeholder="What's your task?"
          className="w-full p-4 border border-gray-300 rounded-lg shadow mb-4"
        />
        <button onClick={handleTaskQuery} className={`${buttonClass} bg-blue-600 hover:bg-blue-700`}>
          Submit Task
        </button>
        {taskList.length > 0 && (
          <div className="mt-6 space-y-4">
            <h3 className="font-semibold text-lg">Task List</h3>
            {taskList.map((task) => (
              <div key={task.id} className="bg-white p-3 rounded-lg shadow text-gray-700 flex justify-between items-center">
                <p className="font-medium">{task.query}</p>
                <button onClick={() => completeTask(task.id)} className={`${buttonClass} bg-green-500 hover:bg-green-600 px-3 py-1`}>
                  ✅ Complete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
