const API_BASE = "http://localhost:8000/api";

// --- Projects ---
export async function getProjects() {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function createProject(data) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function deleteProject(id) {
  const res = await fetch(`${API_BASE}/projects/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete project");
  return res.json();
}

// --- Targets ---
export async function getTargets(projectId) {
  const url = projectId
    ? `${API_BASE}/targets?project_id=${projectId}`
    : `${API_BASE}/targets`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch targets");
  return res.json();
}

export async function createTarget(projectId, data) {
  const res = await fetch(`${API_BASE}/targets?project_id=${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create target");
  return res.json();
}

// --- Vulnerabilities ---
export async function getVulnerabilities(projectId, targetId) {
  let url = `${API_BASE}/vulnerabilities`;
  const params = [];
  if (projectId) params.push(`project_id=${projectId}`);
  if (targetId) params.push(`target_id=${targetId}`);
  if (params.length) url += `?${params.join("&")}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch vulnerabilities");
  return res.json();
}

export async function createVulnerability(projectId, data) {
  const res = await fetch(
    `${API_BASE}/vulnerabilities?project_id=${projectId}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) throw new Error("Failed to create vulnerability");
  return res.json();
}

// --- Reports ---
export async function getReport(projectId) {
  const res = await fetch(`${API_BASE}/reports/${projectId}`);
  if (!res.ok) throw new Error("Failed to fetch report");
  return res.json();
}
