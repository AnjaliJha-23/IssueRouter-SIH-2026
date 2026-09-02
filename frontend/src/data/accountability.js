const HOUR = 60 * 60 * 1000

function svgDataUri(title, subtitle, palette, accent = '#ffffff') {
    const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${palette[0]}" />
          <stop offset="100%" stop-color="${palette[1]}" />
        </linearGradient>
        <linearGradient id="shine" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="rgba(255,255,255,0.32)" />
          <stop offset="100%" stop-color="rgba(255,255,255,0)" />
        </linearGradient>
      </defs>
      <rect width="640" height="420" rx="34" fill="url(#bg)" />
      <circle cx="520" cy="86" r="130" fill="rgba(255,255,255,0.08)" />
      <circle cx="120" cy="330" r="94" fill="rgba(255,255,255,0.08)" />
      <rect x="34" y="34" width="572" height="352" rx="26" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.22)" />
      <rect x="60" y="68" width="180" height="14" rx="7" fill="url(#shine)" />
      <rect x="60" y="96" width="280" height="10" rx="5" fill="rgba(255,255,255,0.42)" />
      <rect x="60" y="128" width="300" height="164" rx="18" fill="rgba(17,24,39,0.18)" stroke="rgba(255,255,255,0.16)" />
      <path d="M94 262L151 215L194 246L246 178L335 262" fill="none" stroke="${accent}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" />
      <circle cx="151" cy="215" r="10" fill="${accent}" opacity="0.95" />
      <circle cx="194" cy="246" r="10" fill="${accent}" opacity="0.95" />
      <circle cx="246" cy="178" r="10" fill="${accent}" opacity="0.95" />
      <circle cx="335" cy="262" r="10" fill="${accent}" opacity="0.95" />
      <rect x="398" y="128" width="172" height="24" rx="12" fill="rgba(255,255,255,0.14)" />
      <rect x="398" y="166" width="134" height="16" rx="8" fill="rgba(255,255,255,0.36)" />
      <rect x="398" y="194" width="156" height="16" rx="8" fill="rgba(255,255,255,0.28)" />
      <rect x="398" y="222" width="118" height="16" rx="8" fill="rgba(255,255,255,0.28)" />
      <rect x="398" y="258" width="172" height="52" rx="18" fill="rgba(255,255,255,0.16)" />
      <text x="60" y="344" fill="#fff" font-size="28" font-family="Arial, Helvetica, sans-serif" font-weight="700">${title}</text>
      <text x="60" y="372" fill="rgba(255,255,255,0.82)" font-size="18" font-family="Arial, Helvetica, sans-serif">${subtitle}</text>
    </svg>`
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

function makePhoto(id, title, subtitle, palette, category) {
    return {
        id,
        title,
        subtitle,
        category,
        src: svgDataUri(title, subtitle, palette),
    }
}

const now = Date.now()

export const ACCOUNTABILITY_BY_CLUSTER = {
    'CLU-0031': {
        assigned_at: new Date(now - 18 * HOUR).toISOString(),
        due_at: new Date(now + 54 * HOUR).toISOString(),
        officer_notes: 'Pump crew inspected the underpass outlet and uploaded the floodline photographs.',
        officer_photos: [
            makePhoto('CLU-0031-1', 'Underpass Waterline', 'Field officer image 01', ['#1d4ed8', '#38bdf8'], 'inspection'),
            makePhoto('CLU-0031-2', 'Drain Outflow', 'Field officer image 02', ['#0f766e', '#14b8a6'], 'inspection'),
            makePhoto('CLU-0031-3', 'Pump Setup', 'Field officer image 03', ['#7c3aed', '#c084fc'], 'inspection'),
        ],
    },
    'CLU-0061': {
        assigned_at: new Date(now - 12 * HOUR).toISOString(),
        due_at: new Date(now + 60 * HOUR).toISOString(),
        officer_notes: 'Water tanker dispatch team shared tanker photos and valve readings.',
        officer_photos: [
            makePhoto('CLU-0061-1', 'Tanker Dispatch', 'Water supply photo 01', ['#0f766e', '#22c55e'], 'dispatch'),
            makePhoto('CLU-0061-2', 'Valve Inspection', 'Water supply photo 02', ['#1d4ed8', '#60a5fa'], 'dispatch'),
        ],
    },
    'CLU-0029': {
        assigned_at: new Date(now - 30 * HOUR).toISOString(),
        due_at: new Date(now + 42 * HOUR).toISOString(),
        officer_notes: 'Site team uploaded boundary markings and encroachment evidence.',
        officer_photos: [
            makePhoto('CLU-0029-1', 'Encroachment Marked', 'Site evidence 01', ['#b45309', '#f59e0b'], 'evidence'),
            makePhoto('CLU-0029-2', 'Road Width Check', 'Site evidence 02', ['#ef4444', '#fb7185'], 'evidence'),
            makePhoto('CLU-0029-3', 'Notice Board', 'Site evidence 03', ['#374151', '#9ca3af'], 'evidence'),
        ],
    },
    'CLU-0073': {
        resolved_at: new Date(now - 6 * HOUR).toISOString(),
        resolved_photos: [
            makePhoto('CLU-0073-r1', 'Sewage Cleared', 'Resolved issue photo 01', ['#0f172a', '#14b8a6'], 'resolved'),
            makePhoto('CLU-0073-r2', 'Drain Restored', 'Resolved issue photo 02', ['#1d4ed8', '#38bdf8'], 'resolved'),
        ],
    },
    'CLU-0066': {
        resolved_at: new Date(now - 10 * HOUR).toISOString(),
        resolved_photos: [
            makePhoto('CLU-0066-r1', 'Power Line Cleared', 'Resolved issue photo 01', ['#4338ca', '#818cf8'], 'resolved'),
            makePhoto('CLU-0066-r2', 'Tree Removal', 'Resolved issue photo 02', ['#166534', '#4ade80'], 'resolved'),
        ],
    },
    'CLU-0115': {
        resolved_at: new Date(now - 14 * HOUR).toISOString(),
        resolved_photos: [
            makePhoto('CLU-0115-r1', 'Bus Stop Restored', 'Resolved issue photo 01', ['#7c2d12', '#fb923c'], 'resolved'),
            makePhoto('CLU-0115-r2', 'Route Back On Time', 'Resolved issue photo 02', ['#0f766e', '#5eead4'], 'resolved'),
        ],
    },
}

export function enrichClusterWithAccountability(cluster) {
    return {
        ...cluster,
        ...(ACCOUNTABILITY_BY_CLUSTER[cluster.cluster_id] ?? {}),
    }
}
