import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogoIcon } from "./SportIcon";

const AVATAR_COLORS = [
  "#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48",
  "#0d9488", "#a16207", "#6d28d9",
];

function avatarColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/feed" className="navbar-brand">
          <LogoIcon size={28} />
          <span>RunBanditsRun</span>
        </Link>

        {user && (
          <div className="navbar-links">
            <NavLink to="/feed" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              <span>Feed</span>
            </NavLink>
            <NavLink to="/explore" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              <span>Explore</span>
            </NavLink>
            <NavLink to="/segments" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
              <span>Segments</span>
            </NavLink>
            <NavLink to="/log" className={({ isActive }) => `nav-link nav-log-btn${isActive ? " active" : ""}`}>
              Log Activity
            </NavLink>

            <div className="nav-user">
              <Link to="/profile" className="nav-avatar-link" title="Profile">
                <div className="avatar avatar-sm" style={{ background: avatarColor(user.username ?? "") }}>
                  {user.username?.[0]?.toUpperCase() ?? "?"}
                </div>
              </Link>
              <button className="btn-ghost btn-sm" onClick={handleLogout}>Log out</button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
