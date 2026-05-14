import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getFeed } from "../api/feed";
import { useAuth } from "../context/AuthContext";
import ActivityCard from "../components/ActivityCard";
import { HERO_IMAGES, EMPTY_STATE_IMAGES } from "../constants/images";

const PAGE_SIZE = 20;

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

export default function Feed() {
  const { user } = useAuth();
  const [extraActivities, setExtraActivities] = useState([]);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const { data: firstPage, isLoading, isError } = useQuery({
    queryKey: ["feed", 0],
    queryFn: () => getFeed(0),
  });

  const allActivities = [...(firstPage ?? []), ...extraActivities];

  const loadMore = useCallback(async () => {
    setLoadingMore(true);
    try {
      const more = await getFeed(allActivities.length);
      setExtraActivities((prev) => [...prev, ...more]);
      setHasMore(more.length >= PAGE_SIZE);
    } finally {
      setLoadingMore(false);
    }
  }, [allActivities.length]);

  return (
    <div className="page">
      <div className="feed-hero" style={{ backgroundImage: `url(${HERO_IMAGES.feed})` }}>
        <div className="feed-hero-overlay">
          <h2 className="feed-greeting">
            {getGreeting()}, {user?.username?.split("_")[0]}
          </h2>
          <p className="feed-sub">Here's what your network has been up to.</p>
        </div>
      </div>

      {isLoading && (
        <>
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
        </>
      )}

      {isError && <div className="error">Failed to load feed. Please try again.</div>}

      {!isLoading && allActivities.length === 0 && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-image">
              <img src={EMPTY_STATE_IMAGES.noActivities} alt="Start your journey" />
            </div>
            <h3>No activities yet</h3>
            <p>Add some friends or log your first activity to get started!</p>
            <Link to="/log" className="btn-primary">Log Your First Activity</Link>
          </div>
        </div>
      )}

      {allActivities.map((activity, i) => (
        <ActivityCard
          key={activity.id}
          activity={activity}
          queryKey={["feed", 0]}
          style={{ animationDelay: `${Math.min(i, 5) * 60}ms` }}
        />
      ))}

      {hasMore && allActivities.length > 0 && (
        <div className="load-more">
          <button onClick={loadMore} disabled={loadingMore}>
            {loadingMore ? "Loading..." : "Load More"}
          </button>
        </div>
      )}
    </div>
  );
}
