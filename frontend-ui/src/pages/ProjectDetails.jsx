import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getTargets, createTarget, getVulnerabilities, createVulnerability } from "../services/api";
import "./ProjectDetails.css";

function ProjectDetails() {
  const { id } = useParams();
  const projectId = parseInt(id, 10);

  const [targets, setTargets] = useState([]);
  const [vulns, setVulns] = useState([]);
  const [loading, setLoading] = useState(true);

  // Forms
  const [showTargetForm, setShowTargetForm] = useState(false);
  const [targetData, setTargetData] = useState({ name: "", type: "Server", description: "", criticality: 5 });

  const [showVulnForm, setShowVulnForm] = useState(false);
  const [vulnData, setVulnData] = useState({ title: "", description: "", severity: "Medium", status: "Open", target_id: "" });

  const fetchData = async () => {
    try {
      const [tData, vData] = await Promise.all([
        getTargets(projectId),
        getVulnerabilities(projectId)
      ]);
      setTargets(tData);
      setVulns(vData);
    } catch {
      console.error("Failed to fetch project details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const handleTargetSubmit = async (e) => {
    e.preventDefault();
    if (!targetData.name) return;
    try {
      await createTarget(projectId, targetData);
      setTargetData({ name: "", type: "Server", description: "", criticality: 5 });
      setShowTargetForm(false);
      fetchData();
    } catch {
      console.error("Failed to add target");
    }
  };

  const handleVulnSubmit = async (e) => {
    e.preventDefault();
    if (!vulnData.title) return;
    try {
      const payload = { ...vulnData, target_id: vulnData.target_id ? parseInt(vulnData.target_id) : null };
      await createVulnerability(projectId, payload);
      setVulnData({ title: "", description: "", severity: "Medium", status: "Open", target_id: "" });
      setShowVulnForm(false);
      fetchData();
    } catch {
      console.error("Failed to add vulnerability");
    }
  };

  if (loading) return <div className="page-loading">Yükleniyor...</div>;

  return (
    <div className="project-details">
      <div className="page-header">
        <div>
          <Link to="/projects" className="back-link">← Projelere Dön</Link>
          <h1 className="page-title">Proje Detayları (ID: {projectId})</h1>
        </div>
      </div>

      <div className="split-view">
        {/* TARGETS SECTION */}
        <section className="detail-section">
          <div className="section-header">
            <h2>Hedefler (Targets)</h2>
            <button className="btn-secondary" onClick={() => setShowTargetForm(!showTargetForm)}>
              {showTargetForm ? "Kapat" : "+ Hedef Ekle"}
            </button>
          </div>

          {showTargetForm && (
            <form className="inline-form" onSubmit={handleTargetSubmit}>
              <input type="text" placeholder="IP veya Domain (Örn: 192.168.1.1)" value={targetData.name} onChange={e => setTargetData({...targetData, name: e.target.value})} required className="form-input" />
              <select value={targetData.type} onChange={e => setTargetData({...targetData, type: e.target.value})} className="form-input">
                <option value="Server">Server</option>
                <option value="WebApp">WebApp</option>
                <option value="API">API</option>
                <option value="Network">Network Kapsamı</option>
              </select>
              <button type="submit" className="btn-primary">Ekle</button>
            </form>
          )}

          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Hedef</th>
                <th>Tip</th>
              </tr>
            </thead>
            <tbody>
              {targets.length === 0 ? (
                <tr><td colSpan="3" align="center" className="empty-cell">Hedef bulunamadı.</td></tr>
              ) : (
                targets.map(t => (
                  <tr key={t.id}>
                    <td className="cell-id">{t.id}</td>
                    <td className="cell-name">{t.name}</td>
                    <td>{t.type}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>

        {/* VULNS SECTION */}
        <section className="detail-section">
          <div className="section-header">
            <h2>Zafiyetler</h2>
            <button className="btn-secondary" onClick={() => setShowVulnForm(!showVulnForm)}>
              {showVulnForm ? "Kapat" : "+ Zafiyet Ekle"}
            </button>
          </div>

          {showVulnForm && (
            <form className="inline-form" onSubmit={handleVulnSubmit}>
              <input type="text" placeholder="Zafiyet Başlığı" value={vulnData.title} onChange={e => setVulnData({...vulnData, title: e.target.value})} required className="form-input" />
              
              <select value={vulnData.severity} onChange={e => setVulnData({...vulnData, severity: e.target.value})} className="form-input">
                <option value="Critical">Critical (Kritik)</option>
                <option value="High">High (Yüksek)</option>
                <option value="Medium">Medium (Orta)</option>
                <option value="Low">Low (Düşük)</option>
                <option value="Info">Info (Bilgilendirme)</option>
              </select>

              <select value={vulnData.target_id} onChange={e => setVulnData({...vulnData, target_id: e.target.value})} className="form-input">
                <option value="">Hedef Seç (Opsiyonel)</option>
                {targets.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
              </select>

              <button type="submit" className="btn-primary">Ekle</button>
            </form>
          )}

          <table className="data-table">
            <thead>
              <tr>
                <th>Risk</th>
                <th>Başlık</th>
                <th>Hedef ID</th>
                <th>Durum</th>
              </tr>
            </thead>
            <tbody>
              {vulns.length === 0 ? (
                <tr><td colSpan="4" align="center" className="empty-cell">Zafiyet kaydı yok.</td></tr>
              ) : (
                vulns.map(v => (
                  <tr key={v.id}>
                    <td>
                      <span className={`badge badge-${v.severity.toLowerCase()}`}>
                        {v.severity}
                      </span>
                    </td>
                    <td className="cell-name">{v.title}</td>
                    <td>{v.target_id || "—"}</td>
                    <td>{v.status}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}

export default ProjectDetails;
