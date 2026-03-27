import { NavLink } from "react-router-dom";
import "./Sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-logo">🛡️</span>
        <h2>SecuLog</h2>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" end className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
          <span className="nav-icon">📊</span>
          <span className="nav-label">Dashboard</span>
        </NavLink>

        <NavLink to="/projects" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
          <span className="nav-icon">📁</span>
          <span className="nav-label">Projeler</span>
        </NavLink>

        <NavLink to="/report" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
          <span className="nav-icon">📋</span>
          <span className="nav-label">Raporlar</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <p>SecuLog-Local v1.0</p>
      </div>
    </aside>
  );
}

export default Sidebar;
