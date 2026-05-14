import { useAuth } from "../context/AuthContext";

const AVATAR_COLORS = [
  "#fc4c02", "#16a34a", "#0284c7", "#9333ea", "#e11d48",
  "#0d9488", "#a16207", "#6d28d9",
];

function fmt(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function Medal({ rank }) {
  if (rank === 1) return <span className="medal medal-gold">1</span>;
  if (rank === 2) return <span className="medal medal-silver">2</span>;
  if (rank === 3) return <span className="medal medal-bronze">3</span>;
  return <span className="leaderboard-rank">{rank}</span>;
}

export default function LeaderboardTable({ efforts }) {
  const { user } = useAuth();

  if (!efforts?.length) {
    return <p style={{ color: "var(--text-muted)", fontSize: "var(--text-sm)" }}>No efforts yet.</p>;
  }

  return (
    <table className="leaderboard">
      <thead>
        <tr>
          <th style={{ width: 48 }}>#</th>
          <th>Athlete</th>
          <th>Time</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        {efforts.map((e) => (
          <tr key={e.athlete_id} className={e.athlete_id === user?.id ? "leaderboard-me" : ""}>
            <td><Medal rank={e.rank} /></td>
            <td>
              <div className="leaderboard-athlete">
                <div
                  className="avatar avatar-sm"
                  style={{ background: AVATAR_COLORS[e.athlete_id % AVATAR_COLORS.length] }}
                >
                  {e.athlete_name?.[0]?.toUpperCase() ?? "?"}
                </div>
                {e.athlete_name}
              </div>
            </td>
            <td className="leaderboard-time">{fmt(e.best_time)}</td>
            <td style={{ color: "var(--text-muted)", fontSize: "var(--text-xs)" }}>—</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
