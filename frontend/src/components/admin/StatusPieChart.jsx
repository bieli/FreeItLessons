export const STATUS_NAMES = ['New', 'Doit', 'Help', 'Good', 'Done'];
const COLORS = ['#3366cc', '#dc3912', '#ff9900', '#109618', '#990099'];

/** Counts of the statuses shown in the admin change list (column "status"). */
export function countStatuses(root = document) {
  const counts = Object.fromEntries(STATUS_NAMES.map((name) => [name, 0]));
  root.querySelectorAll('#result_list tbody td.field-status').forEach((cell) => {
    const name = cell.textContent.trim();
    if (name in counts) counts[name] += 1;
  });
  return counts;
}

/** SVG path of a pie slice between two angles (radians, clockwise from 12 o'clock). */
export function slicePath(cx, cy, r, start, end) {
  if (end - start >= 2 * Math.PI - 1e-9) {
    return `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx - 0.001} ${cy - r} Z`;
  }
  const point = (angle) => [cx + r * Math.sin(angle), cy - r * Math.cos(angle)];
  const [x1, y1] = point(start);
  const [x2, y2] = point(end);
  const large = end - start > Math.PI ? 1 : 0;
  return `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`;
}

export default function StatusPieChart({ counts, title = 'Content Statuses Activities' }) {
  const total = STATUS_NAMES.reduce((sum, name) => sum + counts[name], 0);
  let angle = 0;
  const slices = STATUS_NAMES.map((name, index) => {
    const value = counts[name];
    const start = angle;
    angle += total ? (value / total) * 2 * Math.PI : 0;
    return { name, value, color: COLORS[index], path: value ? slicePath(150, 150, 140, start, angle) : null };
  });

  return (
    <figure className="status-chart" aria-label={title}>
      <figcaption><strong>{title}</strong></figcaption>
      <svg width="300" height="300" viewBox="0 0 300 300" role="img" aria-label={title}>
        {total === 0 && <circle cx="150" cy="150" r="140" fill="#eee" />}
        {slices.filter((slice) => slice.path).map((slice) => (
          <path key={slice.name} d={slice.path} fill={slice.color} stroke="#fff">
            <title>{`${slice.name}: ${slice.value}`}</title>
          </path>
        ))}
      </svg>
      <ul className="status-chart__legend">
        {slices.map((slice) => (
          <li key={slice.name}>
            <span className="status-chart__swatch" style={{ background: slice.color }} />
            {slice.name}: {slice.value}{total ? ` (${Math.round((slice.value / total) * 100)}%)` : ''}
          </li>
        ))}
      </ul>
    </figure>
  );
}
