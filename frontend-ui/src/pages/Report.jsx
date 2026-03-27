import { useEffect, useState } from "react";
import { getProjects, getReport } from "../services/api";
import "./Report.css";

function Report() {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch {
        console.error("Projeler yüklenemedi");
      }
    }
    init();
  }, []);

  useEffect(() => {
    if (!selectedProjectId) {
      setReportData(null);
      return;
    }
    async function fetchReport() {
      setLoading(true);
      try {
        const data = await getReport(selectedProjectId);
        setReportData(data);
      } catch {
        console.error("Rapor alınamadı");
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [selectedProjectId]);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="report-page">
      <div className="report-header-controls no-print">
        <div>
          <h1 className="page-title">Otomatik Raporlama</h1>
          <p className="page-subtitle">Seçilen sızma testi projesinin veri istatistikleri ve özet çıktısı</p>
        </div>
        <div className="report-actions">
          <select 
            className="form-input project-selector" 
            value={selectedProjectId} 
            onChange={(e) => setSelectedProjectId(e.target.value)}
          >
            <option value="">-- Proje Seçin --</option>
            {projects.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button 
            className="btn-primary" 
            onClick={handlePrint} 
            disabled={!reportData}
          >
            🖨️ PDF / Yazdır
          </button>
        </div>
      </div>

      {loading && <div className="page-loading">Rapor Hazırlanıyor...</div>}

      {!loading && reportData && (
        <div className="report-content" id="printable-report">
          <div className="report-cover">
            <h1 className="report-doc-title">Sızma Testi Bulguları</h1>
            <h2 className="report-doc-project">{reportData.project.name}</h2>
            <p className="report-doc-desc">{reportData.project.description || "Açıklama girilmemiş."}</p>
            <hr className="report-divider" />
          </div>

          <div className="report-stats-grid">
            <div className="r-stat-box">
              <h3>{reportData.total_targets}</h3>
              <p>İncelenen Hedef</p>
            </div>
            <div className="r-stat-box">
              <h3>{reportData.total_vulns}</h3>
              <p>Toplam Bulgu</p>
            </div>
            <div className="r-stat-box" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
              <h3 style={{ color: '#f87171' }}>{reportData.open_vulns}</h3>
              <p>Açık Kapatılmamış</p>
            </div>
          </div>

          <div className="report-severity-bar">
            <h3>Ciddiyet Derecesine Göre Açık Bulgular (Open Status)</h3>
            <div className="sev-row critical"><span className="s-label">Critical</span> <span className="s-val">{reportData.stats.Critical}</span></div>
            <div className="sev-row high"><span className="s-label">High</span> <span className="s-val">{reportData.stats.High}</span></div>
            <div className="sev-row medium"><span className="s-label">Medium</span> <span className="s-val">{reportData.stats.Medium}</span></div>
            <div className="sev-row low"><span className="s-label">Low</span> <span className="s-val">{reportData.stats.Low}</span></div>
            <div className="sev-row info"><span className="s-label">Info</span> <span className="s-val">{reportData.stats.Info}</span></div>
          </div>

          <div className="report-target-details">
            <h2 className="section-title">Hedef Detayları ve Zafiyetler</h2>
            
            {reportData.targets.map(target => (
              <div key={target.id || "genel"} className="target-block">
                <div className="target-header">
                  <h4>{target.name}</h4>
                  <span className="target-type">{target.type}</span>
                </div>
                
                {target.vulnerabilities.length === 0 ? (
                  <p className="no-vuln">Bu hedefe ait kaydedilmiş zafiyet bulunamadı.</p>
                ) : (
                  <ul className="vuln-list">
                    {target.vulnerabilities.map(v => (
                      <li key={v.id}>
                        <span className={`r-badge r-badge-${v.severity.toLowerCase()}`}>{v.severity}</span>
                        <strong className="v-title">{v.title}</strong>
                        <span className="v-status">({v.status})</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>

          <div className="report-footer">
            <p>Bu rapor <strong>SecuLog-Local</strong> sistemi tarafından otomatik olarak oluşturulmuştur.</p>
            <p>Tarih: {new Date().toLocaleDateString('tr-TR')} {new Date().toLocaleTimeString('tr-TR')}</p>
          </div>
        </div>
      )}

      {!loading && !reportData && (
        <div className="placeholder-box no-print">
          <span className="placeholder-icon">📑</span>
          <p>Lütfen önce yukarıdan bir proje seçin.</p>
        </div>
      )}
    </div>
  );
}

export default Report;
