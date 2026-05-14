import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  searchUsers,
  getFriends,
  getIncomingFriendRequests,
  getSentFriendRequests,
  sendFriendRequest,
  acceptFriendRequest,
  removeFriend,
} from "../api/users";
import UserCard from "../components/UserCard";
import { SearchIcon } from "../components/SportIcon";
import { HERO_IMAGES } from "../constants/images";

export default function Social() {
  const [query, setQuery] = useState("");
  const qc = useQueryClient();

  const { data: searchResults } = useQuery({
    queryKey: ["searchUsers", query],
    queryFn: () => searchUsers(query),
    enabled: true,
    refetchInterval: REFETCH_INTERVAL_MS,
  });

  const { data: friends = [] } = useQuery({
    queryKey: ["friends"],
    queryFn: getFriends,
    refetchInterval: REFETCH_INTERVAL_MS,
  });

  const { data: incomingFriendRequests = [] } = useQuery({
    queryKey: ["incomingFriendRequests"],
    queryFn: getIncomingFriendRequests,
    refetchInterval: REFETCH_INTERVAL_MS,
  });

  const { data: sentFriendRequests = [] } = useQuery({
    queryKey: ["sentFriendRequests"],
    queryFn: getSentFriendRequests,
    refetchInterval: REFETCH_INTERVAL_MS,
  });

  const friendIds = new Set(friends.map((u) => u.id));
  const pendingIncomingIds = new Set(incomingFriendRequests.map((r) => r.requester_id));
  const pendingOutgoingIds = new Set(sentFriendRequests.map((r) => r.addressee_id));

  const sendFriendRequestMutation = useMutation({
    mutationFn: sendFriendRequest,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["friends"] });
      qc.invalidateQueries({ queryKey: ["sentFriendRequests"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  const acceptFriendRequestMutation = useMutation({
    mutationFn: acceptFriendRequest,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["friends"] });
      qc.invalidateQueries({ queryKey: ["incomingFriendRequests"] });
      qc.invalidateQueries({ queryKey: ["sentFriendRequests"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  const removeFriendMutation = useMutation({
    mutationFn: removeFriend,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["friends"] });
      qc.invalidateQueries({ queryKey: ["sentFriendRequests"] });
      qc.invalidateQueries({ queryKey: ["incomingFriendRequests"] });
      qc.invalidateQueries({ queryKey: ["searchUsers"] });
    },
  });

  function getStatus(userId) {
    if (friendIds.has(userId)) return "accepted";
    if (pendingIncomingIds.has(userId)) return "incoming";
    if (pendingOutgoingIds.has(userId)) return "pending";
    return null;
  }

  const incoming = incomingFriendRequests;

  // Build connections list: friends + sent requests
  const connections = [
    ...friends.map((f) => ({ ...f, status: "accepted" })),
    ...sentFriendRequests.map((req) => ({
      ...req.addressee,
      status: "pending",
      requestId: req.id,
    })),
  ];



  return (
    <div className="page social-page">
      <div className="social-hero" style={{ backgroundImage: `url(${HERO_IMAGES.explore})` }}>
        <div className="social-hero-overlay">
          <h2>Social</h2>
          <p>Connect with friends</p>
        </div>
      </div>

      <div className="friends-section">
        <h3 className="section-title">Your Connections</h3>
        {connections.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>No connections yet. Search for athletes to connect.</p>
        ) : (
          <div className="friends-grid">
            {connections.map((user) => (
              <UserCard
                key={user.id}
                user={user}
                status={user.status}
                onUnfollow={() => removeFriendMutation.mutate(user.id)}
                onCancel={() => removeFriendMutation.mutate(user.id)}
                loading={removeFriendMutation.isPending}
              />
            ))}
          </div>
        )}
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

      {incoming.length > 0 && !query && (
        <div style={{ marginBottom: 32 }}>
          <h3 className="section-title">Friend Requests</h3>
          {incoming.map((req) => (
            <UserCard
              key={req.requester_id}
              user={req.requester}
              status="incoming"
              onAccept={() => acceptFriendRequestMutation.mutate(req.requester_id)}
              loading={acceptFriendRequestMutation.isPending}
            />
          ))}
        </div>
      )}

      {searchResults?.length > 0 && (
        <>
          <h3 className="section-title">{query ? "Search Results" : "Suggested Athletes"}</h3>
          {searchResults?.map((u) => (
            <UserCard
              key={u.id}
              user={u}
              status={query ? getStatus(u.id) : null}
              onFollow={() => sendFriendRequestMutation.mutate(u.id)}
              onAccept={() => acceptFriendRequestMutation.mutate(u.id)}
              loading={sendFriendRequestMutation.isPending || acceptFriendRequestMutation.isPending}
            />
          ))}
        </>
      )}
      {searchResults?.length === 0 && query && (
        <p style={{ color: "var(--text-muted)", fontSize: "var(--text-sm)" }}>
          No athletes found.
        </p>
      )}
    </div>
  );
}
