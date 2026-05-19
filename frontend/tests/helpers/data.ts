let counter = 0;

export function unique(prefix = "t") {
  return `${prefix}_${counter++}_${Date.now()}`;
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

export function commonActivityPayload(overrides = {}) {
  return {
    name: unique("CommonActivity"),
    sport_type: "run",
    polyline: "_p~iF~ps|U_ulLnnqC_mqNvxq`@",
    ...overrides,
  };
}
