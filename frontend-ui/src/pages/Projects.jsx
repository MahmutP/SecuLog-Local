import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProjects, createProject, deleteProject } from "../services/api";
import "./Projects.css";

function Projects() {
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: "", description: "" });
  const [loading, setLoading] = useState(true);

  const fetchProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch {
      console.error("Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) return;
    try {
      await createProject(formData);
      setFormData({ name: "", description: "" });
      setShowForm(false);
      fetchProjects();
    } catch {
      console.error("Failed to create project");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bu projeyi silmek istediğinize emin misiniz?")) return;
    try {
      await deleteProject(id);
      fetchProjects();
    } catch {
      console.error("Failed to delete project");
    }
  };

  if (loading) return <div className="page-loading">Yükleniyor...</div>;

  return (
    <div className="projects-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Projeler</h1>
          <p className="page-subtitle">Tüm sızma testi projelerinizi yönetin</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "İptal" : "+ Yeni Proje"}
        </button>
      </div>

      {showForm && (
        <form className="project-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Proje Adı"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="form-input"
            required
          />
          <textarea
            placeholder="Açıklama (opsiyonel)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="form-input form-textarea"
            rows={3}
          />
          <button type="submit" className="btn-primary">Kaydet</button>
        </form>
      )}

      {projects.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">📂</span>
          <p>Henüz proje yok. Yukarıdaki butona tıklayarak yeni bir proje oluşturun.</p>
        </div>
      ) : (
        <div className="projects-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Proje Adı</th>
                <th>Açıklama</th>
                <th>Oluşturulma</th>
                <th>İşlem</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id}>
                  <td className="cell-id">{p.id}</td>
                  <td className="cell-name">{p.name}</td>
                  <td className="cell-desc">{p.description || "—"}</td>
                  <td className="cell-date">{new Date(p.created_at).toLocaleDateString("tr-TR")}</td>
                  <td>
                    <Link to={`/project/${p.id}`} className="btn-secondary-link">Detay</Link>
                    <button className="btn-danger-sm" onClick={() => handleDelete(p.id)} style={{ marginLeft: "8px" }}>Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Projects;
