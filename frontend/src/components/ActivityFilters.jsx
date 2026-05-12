const SPORTS = [
  { value: "all", label: "All" },
  { value: "run", label: "Run" },
  { value: "ride", label: "Ride" },
  { value: "swim", label: "Swim" },
  { value: "walk", label: "Walk" },
  { value: "hike", label: "Hike" },
];

export default function ActivityFilters({ selected, onChange }) {
  return (
    <div className="filter-pills">
      {SPORTS.map((s) => (
        <button
          key={s.value}
          className={`filter-pill${selected === s.value ? " active" : ""}`}
          onClick={() => onChange(s.value)}
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}
