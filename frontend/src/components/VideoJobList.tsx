// frontend/src/components/VideoJobList.tsx
import React, { useEffect, useState } from "react";
import {
  JobStatusResponse,
  getJobStatus,
  getVideoDownloadUrl,
} from "../api/client";

interface Props {
  jobIds: string[];
}

const POLL_INTERVAL = 3000; // 3 seconds

const VideoJobList: React.FC<Props> = ({ jobIds }) => {
  const [jobs, setJobs] = useState<Record<string, JobStatusResponse>>({});

  useEffect(() => {
    let timer: number | undefined;

    const poll = async () => {
      if (jobIds.length === 0) return;
      try {
        const updates: Record<string, JobStatusResponse> = {};
        for (const id of jobIds) {
          const status = await getJobStatus(id);
          updates[id] = status;
        }
        setJobs((prev) => ({ ...prev, ...updates }));
      } catch (err) {
        console.error("Polling error:", err);
      } finally {
        timer = window.setTimeout(poll, POLL_INTERVAL);
      }
    };

    if (jobIds.length > 0) {
      poll();
    }

    return () => {
      if (timer) window.clearTimeout(timer);
    };
  }, [jobIds]);

  if (jobIds.length === 0) return null;

  return (
    <div className="job-list">
      <h3>Your Videos</h3>
      {jobIds.map((id) => {
        const job = jobs[id];
        const statusClass = job?.status || "unknown";

        return (
          <div key={id} className={`job-item status-${statusClass}`}>
            <div className="job-header">
              <div className="job-id">Job ID: {id.substring(0, 8)}...</div>
              <div className={`job-status ${statusClass}`}>
                {job?.status ?? "unknown"}
              </div>
            </div>

            <div className="job-message">{job?.message || "Initializing..."}</div>

            {job?.status === "done" && (
              <div className="job-video">
                <video
                  src={
                    job.video_url
                      ? `http://localhost:8081${job.video_url}`
                      : getVideoDownloadUrl(id)
                  }
                  controls
                  width={480}
                  height={360}
                />
                <div className="job-actions">
                  <a
                    href={getVideoDownloadUrl(id)}
                    download
                    className="btn-download"
                  >
                    Download
                  </a>
                </div>
              </div>
            )}

            {job?.status === "failed" && (
              <div className="job-error">Error: {job.message}</div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default VideoJobList;
