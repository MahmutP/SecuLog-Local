import { useEffect, useState } from "react";
import { getProjects, getTargets, getVulnerabilities } from "../services/api";
import "./Dashboard.css";

function Dashboard() {
  const [stats, setStats] = useState({ projects: 0, targets: 0, vulns: 0, openVulns: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const [projects, targets, vulns] = await Promise.all([
          getProjects(),
          getTargets(),
          getVulnerabilities(),
        ]);
        const openVulns = vulns.filter((v) => v.status === "Open").length;
        setStats({
          projects: projects.length,
          targets: targets.length,
          vulns: vulns.length,
          openVulns,
        });
      } catch {
        console.error("Stats fetch failed");
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) return <div className="page-loading">Yükleniyor...</div>;

  return (
    <div className="dashboard">
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">SecuLog-Local genel bakış</p>

      <div className="cards-grid">
        <div className="stat-card card-projects">
          <span className="card-icon">📁</span>
          <div className="card-info">
            <span className="card-number">{stats.projects}</span>
            <span className="card-label">Toplam Proje</span>
          </div>
        </div>

        <div className="stat-card card-targets">
          <span className="card-icon">🎯</span>
          <div className="card-info">
            <span className="card-number">{stats.targets}</span>
            <span className="card-label">Toplam Hedef</span>
          </div>
        </div>

        <div className="stat-card card-vulns">
          <span className="card-icon">🐛</span>
          <div className="card-info">
            <span className="card-number">{stats.vulns}</span>
            <span className="card-label">Toplam Zafiyet</span>
          </div>
        </div>

        <div className="stat-card card-open">
          <span className="card-icon">🔓</span>
          <div className="card-info">
            <span className="card-number">{stats.openVulns}</span>
            <span className="card-label">Açık Zafiyet</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
