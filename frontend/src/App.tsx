import React, { useState } from "react";
import PromptForm from "./components/PromptForm";
import VideoJobList from "./components/VideoJobList";
import "./styles/main.css";

const App: React.FC = () => {
  const [jobIds, setJobIds] = useState<string[]>([]);

  const handleJobCreated = (jobId: string) => {
    setJobIds((prev) => [jobId, ...prev]);
  };

  return (
    <div className="app-root">
      <h1>AI Video Generator (Prototype)</h1>
      <PromptForm onJobCreated={handleJobCreated} />
      <VideoJobList jobIds={jobIds} />
    </div>
  );
};

export default App;
