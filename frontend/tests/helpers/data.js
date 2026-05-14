export function unique(prefix = "t") {
  return `${prefix}_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
}

export function activityPayload(overrides = {}) {
  return {
    title: unique("Activity"),
    sport_type: "run",
    distance: 5,
    duration: 30,
    elevation: 50,
    visibility: "public",
    ...overrides,
  };
}

export function segmentPayload(overrides = {}) {
  return {
    name: unique("Segment"),
    distance: 2,
    ...overrides,
  };
}
