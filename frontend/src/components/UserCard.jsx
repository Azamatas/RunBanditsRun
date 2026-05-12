const AVATAR_COLORS = [
  "#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48",
  "#0d9488", "#a16207", "#6d28d9",
];

export default function UserCard({ user, status, onFollow, onAccept, loading }) {
  const color = AVATAR_COLORS[user.id % AVATAR_COLORS.length];

  let actionBtn;
  if (status === "accepted") {
    actionBtn = <button className="btn-ghost btn-sm follow-btn follow-btn-following" disabled>Following</button>;
  } else if (status === "pending") {
    actionBtn = <button className="btn-sm follow-btn follow-btn-pending" disabled>Pending</button>;
  } else if (status === "incoming") {
    actionBtn = (
      <button className="btn-primary btn-sm follow-btn" onClick={onAccept} disabled={loading}>
        Accept
      </button>
    );
  } else {
    actionBtn = (
      <button className="btn-primary btn-sm follow-btn" onClick={onFollow} disabled={loading}>
        Follow
      </button>
    );
  }

  return (
    <div className="user-card">
      <div className="avatar" style={{ background: color }}>
        {user.username[0].toUpperCase()}
      </div>
      <div className="user-card-info">
        <div className="user-card-name">{user.username}</div>
        {user.location && <div className="user-card-location">{user.location}</div>}
        {user.bio && <div className="user-card-bio">{user.bio}</div>}
      </div>
      {actionBtn}
    </div>
  );
}
