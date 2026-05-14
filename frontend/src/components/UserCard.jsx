import { Link } from "react-router-dom";

const AVATAR_COLORS = [
  "#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48",
  "#0d9488", "#a16207", "#6d28d9",
];

export default function UserCard({ user, status, onFollow, onAccept, onUnfollow, loading }) {
  const color = AVATAR_COLORS[user.id % AVATAR_COLORS.length];

  let actionBtn;
  if (status === "accepted") {
    actionBtn = <button className="btn-ghost btn-sm friend-btn friend-btn-accepted" onClick={onUnfollow} disabled={loading}>Friends</button>;
  } else if (status === "pending") {
    actionBtn = <button className="btn-sm friend-btn friend-btn-pending" disabled>Request Sent</button>;
  } else if (status === "incoming") {
    actionBtn = (
      <button className="btn-primary btn-sm friend-btn" onClick={onAccept} disabled={loading}>
        Accept
      </button>
    );
  } else {
    actionBtn = (
      <button className="btn-primary btn-sm friend-btn" onClick={onFollow} disabled={loading}>
        Add Friend
      </button>
    );
  }

  return (
    <div className="user-card">
      <Link to={`/users/${user.id}`} className="avatar" style={{ background: color, textDecoration: "none" }}>
        {user.username[0].toUpperCase()}
      </Link>
      <Link to={`/users/${user.id}`} className="user-card-info" style={{ textDecoration: "none", color: "inherit" }}>
        <div className="user-card-name">{user.username}</div>
        {user.location && <div className="user-card-location">{user.location}</div>}
        {user.bio && <div className="user-card-bio">{user.bio}</div>}
      </Link>
      {actionBtn}
    </div>
  );
}
