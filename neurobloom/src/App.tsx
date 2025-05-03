// src/App.jsx
import { useState } from 'react';
import Webcam from "react-webcam";

export default function App() {
  const [emotion, setEmotion] = useState("Neutral");
  const [journal, setJournal] = useState("");
  const [tasks, setTasks] = useState([]);
  const [taskInput, setTaskInput] = useState("");

  const mockDetectEmotion = () => {
    const emotions = ["Happy", "Sad", "Neutral", "Angry", "Surprised"];
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    setEmotion(randomEmotion);
  };

  const handleAddTask = () => {
    if (taskInput.trim()) {
      setTasks([...tasks, { text: taskInput, done: false }]);
      setTaskInput("");
    }
  };

  const handleToggleTask = (index) => {
    const updated = [...tasks];
    updated[index].done = !updated[index].done;
    setTasks(updated);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 to-blue-100 p-4 text-gray-800">
      <h1 className="text-3xl font-bold text-center mb-6">Neurobloom 🌸</h1>

      {/* Webcam + Emotion */}
      <div className="flex flex-col items-center gap-4 mb-8">
        <Webcam
          className="rounded-lg shadow-md w-64 h-48"
          screenshotFormat="image/jpeg"
        />
        <button
          onClick={mockDetectEmotion}
          className="px-4 py-2 bg-indigo-600 text-white rounded-xl shadow"
        >
          Analyze Emotion
        </button>
        <div className="text-xl">Detected Emotion: <span className="font-semibold">{emotion}</span></div>
        <div className="italic text-sm text-gray-600">Suggested Action: {emotion === "Happy" ? "Keep up the momentum!" : emotion === "Sad" ? "Play a comforting video." : emotion === "Angry" ? "Try breathing exercise." : emotion === "Surprised" ? "Log this moment." : "Stay focused."}</div>
      </div>

      {/* Task Manager */}
      <div className="mb-10">
        <h2 className="text-xl font-bold mb-2">🎯 Tasks</h2>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            className="flex-1 p-2 rounded border"
            placeholder="New task..."
          />
          <button
            onClick={handleAddTask}
            className="px-4 py-2 bg-green-500 text-white rounded"
          >Add</button>
        </div>
        <ul className="space-y-2">
          {tasks.map((task, i) => (
            <li
              key={i}
              onClick={() => handleToggleTask(i)}
              className={`p-2 rounded cursor-pointer ${task.done ? 'line-through text-gray-400' : 'bg-white shadow'}`}
            >
              {task.text}
            </li>
          ))}
        </ul>
      </div>

      {/* Journal */}
      <div>
        <h2 className="text-xl font-bold mb-2">📝 Journal</h2>
        <textarea
          value={journal}
          onChange={(e) => setJournal(e.target.value)}
          className="w-full h-40 p-2 rounded border"
          placeholder="Write about your day, thoughts, or feelings..."
        ></textarea>
      </div>
    </div>
  );
}
