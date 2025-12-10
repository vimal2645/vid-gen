import React, { useState } from "react";
import { generateVideo } from "../api/client";

interface Props {
  onJobCreated: (jobId: string) => void;
}

const PromptForm: React.FC<Props> = ({ onJobCreated }) => {
  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState(10);
  const [refine, setRefine] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      alert("Please enter a prompt");
      return;
    }

    setLoading(true);
    try {
      const res = await generateVideo({
        prompt,
        duration_seconds: duration,
        refine_with_ai: refine,
      });
      onJobCreated(res.job_id);
      setPrompt("");
      setDuration(10);
    } catch (err) {
      console.error(err);
      alert("Failed to create job");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="prompt-form">
      <div className="form-group">
        <label htmlFor="prompt">Describe your video:</label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., A cinematic shot of a spaceship flying through space..."
          rows={4}
        />
      </div>

      <div className="controls">
        <div className="form-group">
          <label htmlFor="duration">Duration (seconds):</label>
          <input
            id="duration"
            type="number"
            min={3}
            max={60}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
          />
        </div>

        <div className="form-group checkbox">
          <label>
            <input
              type="checkbox"
              checked={refine}
              onChange={(e) => setRefine(e.target.checked)}
            />
            Refine with AI (Groq)
          </label>
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-primary">
        {loading ? "Creating job..." : "Generate Video"}
      </button>
    </form>
  );
};

export default PromptForm;
