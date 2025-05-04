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
  const [journalEntries, setJournalEntries] = useState([]);
  const [taskList, setTaskList] = useState([]); // Task list state
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
      if (result.error) {
        setEmotion("Error");
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
        body: JSON.stringify({ query, sessionId })
      });
  
      const result = await response.json();
      const journalResponse = result.response.content || "No response from journal agent.";
  
      // Save the entry
      setJournalEntries(prev => [...prev, { input: query, response: journalResponse }]);
      setJournalQuery(""); // Clear text field
    } catch (error) {
      console.error("Journal query failed:", error);
      setAgentResponse(`Error: ${error.message}`); // Keep error here optionally
    }
  };

  const handleSimpleJournalSubmit = () => {
    if (!journalQuery.trim()) return;
    setJournalEntries(prev => [...prev, { input: journalQuery, response: "" }]);
    setJournalQuery("");
  };
  
  // Handle Task Query and Add Task to List
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

      // Add task to task list
      const newTask = {
        id: Date.now(),
        query: taskQuery,
        response: result.response || "No response",
        isExecuted: false // Track task execution status
      };

      setTaskList(prev => [...prev, newTask]);
      setTaskQuery(""); // Clear task input
    } catch (error) {
      console.error("Task query failed:", error);
      setAgentResponse(`Error: ${error.message}`);
    }
  };

  // Execute Task
  const executeTask = async (taskId) => {
    try {
      // Find the task to execute
      const task = taskList.find(task => task.id === taskId);
      if (!task) return;

      // Mark the task as executed
      setTaskList(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? { ...task, isExecuted: true } : task
        )
      );

      // Execute the task by calling an API or performing an action
      const response = await fetch("http://localhost:8000/agent/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ taskQuery: task.query, sessionId })
      });

      const result = await response.json();
      setAgentResponse(result.response || "No response from task agent.");
      
      // Optionally, update task execution status or add details here
    } catch (error) {
      console.error("Task execution failed:", error);
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
          value={journalQuery}
          onChange={(e) => setJournalQuery(e.target.value)}
          placeholder="Write something for your journal..."
          className="w-full p-4 border border-gray-300 rounded-lg shadow-md mb-2"
        />
        <button
          onClick={handleSimpleJournalSubmit}
          className="px-4 py-2 bg-green-600 text-white rounded-xl shadow"
        >
          Submit Journal
        </button>
        <button
          onClick={async () => {
            try {
              const response = await fetch("http://localhost:8000/agent/journal", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
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
          className="ml-2 px-4 py-2 bg-purple-600 text-white rounded-xl shadow"
        >
          AI Add to Journal
        </button>

        {/* Display Journal Entries */}
        {journalEntries.length > 0 && (
          <div className="mt-4 space-y-4">
            <h3 className="font-bold text-lg">Journal History</h3>
            {journalEntries.map((entry, index) => (
              <div key={index} className="p-3 bg-white rounded-lg shadow">
                <p className="text-gray-800 font-semibold">You:</p>
                <p className="mb-2 text-gray-700">{entry.input}</p>
              </div>
            ))}
          </div>
        )}
      </div>

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

      {/* Display Task List */}
      <div className="mt-4">
        {taskList.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-bold text-lg">Task List</h3>
            {taskList.map((task) => (
              <div key={task.id} className="p-3 bg-white rounded-lg shadow">
                <p className="text-gray-800 font-semibold">{task.query}</p>
                <button
                  onClick={() => executeTask(task.id)}
                  className="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg"
                >
                  Execute Task
                </button>
                {task.isExecuted && (
                  <p className="mt-2 text-gray-700 text-green-600">Task executed successfully!</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
