import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { searchUsers, getFollowing, getPendingRequests, getSentRequests, followUser, acceptFollow } from "../api/users";
import UserCard from "../components/UserCard";
import { SearchIcon } from "../components/SportIcon";
import { HERO_IMAGES } from "../constants/images";

export default function Explore() {
  const [query, setQuery] = useState("");
  const qc = useQueryClient();

  const { data: searchResults } = useQuery({
    queryKey: ["searchUsers", query],
    queryFn: () => searchUsers(query),
    enabled: true,
  });

  const { data: following } = useQuery({
    queryKey: ["following"],
    queryFn: getFollowing,
  });

  const { data: pendingRequests } = useQuery({
    queryKey: ["pendingRequests"],
    queryFn: getPendingRequests,
  });

  const { data: sentRequests } = useQuery({
    queryKey: ["sentRequests"],
    queryFn: getSentRequests,
  });

  const followingIds = new Set((following ?? []).map((u) => u.id));
  const pendingIncomingIds = new Set((pendingRequests ?? []).map((r) => r.requester_id));
  const pendingOutgoingIds = new Set((sentRequests ?? []).map((r) => r.addressee_id));

  const followMutation = useMutation({
    mutationFn: followUser,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["following"] });
      qc.invalidateQueries({ queryKey: ["sentRequests"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  const acceptMutation = useMutation({
    mutationFn: acceptFollow,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["following"] });
      qc.invalidateQueries({ queryKey: ["pendingRequests"] });
      qc.invalidateQueries({ queryKey: ["sentRequests"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  function getStatus(userId) {
    if (followingIds.has(userId)) return "accepted";
    if (pendingIncomingIds.has(userId)) return "incoming";
    if (pendingOutgoingIds.has(userId)) return "pending";
    return null;
  }

  const incoming = pendingRequests ?? [];

  return (
    <div className="page">
      <div className="explore-hero" style={{ backgroundImage: `url(${HERO_IMAGES.explore})` }}>
        <div className="explore-hero-overlay">
          <h2>Explore Athletes</h2>
          <p>Find and connect with fellow athletes</p>
        </div>
      </div>

      <div className="search-bar">
        <span className="search-bar-icon">
          <SearchIcon size={18} color="var(--text-muted)" />
        </span>
        <input
          placeholder="Search athletes..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {incoming.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 className="section-title">Pending Requests</h3>
          {incoming.map((req) => (
            <UserCard
              key={req.requester_id}
              user={req.requester}
              status="incoming"
              onAccept={() => acceptMutation.mutate(req.requester_id)}
              loading={acceptMutation.isPending}
            />
          ))}
        </div>
      )}

      <h3 className="section-title">{query ? "Search Results" : "Suggested Athletes"}</h3>
      {searchResults?.length === 0 && (
        <p style={{ color: "var(--text-muted)", fontSize: "var(--text-sm)" }}>
          No athletes found.
        </p>
      )}
      {searchResults?.map((u) => (
        <UserCard
          key={u.id}
          user={u}
          status={getStatus(u.id)}
          onFollow={() => followMutation.mutate(u.id)}
          onAccept={() => acceptMutation.mutate(u.id)}
          loading={followMutation.isPending}
        />
      ))}
    </div>
  );
}
