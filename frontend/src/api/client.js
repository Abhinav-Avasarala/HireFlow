const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function analyzeApplication({ resumeFile, jobUrl, jobText }) {
  const formData = new FormData();
  formData.append("resume_pdf", resumeFile);

  if (jobUrl?.trim()) {
    formData.append("job_url", jobUrl.trim());
  }

  if (jobText?.trim()) {
    formData.append("job_text", jobText.trim());
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Failed to analyze application.");
  }

  return response.json();
}

export async function respondToClarification({ sessionId, answer }) {
  const response = await fetch(`${API_BASE_URL}/api/respond`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      answer,
    }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "Failed to generate final output.");
  }

  return response.json();
}
