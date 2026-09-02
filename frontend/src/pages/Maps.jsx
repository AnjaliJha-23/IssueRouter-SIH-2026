import { useEffect, useRef, useState } from 'react'
import useClusters from '../hooks/useClusters'
import { MapPin, Layers, List, TrendingUp, Building2, AlertCircle } from 'lucide-react'

const PRIORITY_COLORS = { 1: '#ef4444', 2: '#f97316', 3: '#6366f1', 4: '#9ca3af' }
const STATUS_STYLES = {
  pending:    'bg-amber-50 text-amber-700',
  inprogress: 'bg-blue-50 text-blue-700',
  resolved:   'bg-green-50 text-green-700',
}
const STATUS_LABELS = { pending: 'Pending', inprogress: 'In progress', resolved: 'Resolved' }

function makeIcon(L, color) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:28px;height:28px;border-radius:50% 50% 50% 0;
      background:${color};border:2px solid white;
      transform:rotate(-45deg);
      box-shadow:0 2px 6px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -30],
  })
}

function popupHTML(c) {
  const color = PRIORITY_COLORS[c.priority] ?? '#9ca3af'
  return `
    <div style="font-family:system-ui,sans-serif;min-width:220px;max-width:260px;">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
        <div style="width:10px;height:10px;border-radius:50%;background:${color};flex-shrink:0;"></div>
        <span style="font-size:12px;font-weight:600;color:#1f2937;line-height:1.3;">${c.problem}</span>
      </div>
      <div style="font-size:11px;color:#6b7280;margin-bottom:10px;line-height:1.5;">${(c.summary ?? '').slice(0, 90)}…</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
        <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px;">
          <div style="font-size:10px;color:#9ca3af;">Complaints</div>
          <div style="font-size:15px;font-weight:600;color:#1f2937;">${c.complaint_count}</div>
        </div>
        <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px;">
          <div style="font-size:10px;color:#9ca3af;">RT reach</div>
          <div style="font-size:15px;font-weight:600;color:#1f2937;">${c.rt_reach?.toLocaleString?.() ?? c.rt_reach}</div>
        </div>
        <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px;">
          <div style="font-size:10px;color:#9ca3af;">Department</div>
          <div style="font-size:13px;font-weight:500;color:#1f2937;">${c.department}</div>
        </div>
        <div style="background:#f3f4f6;border-radius:6px;padding:6px 8px;">
          <div style="font-size:10px;color:#9ca3af;">Priority</div>
          <div style="font-size:13px;font-weight:500;color:${color};">P${c.priority}</div>
        </div>
      </div>
      <div style="font-size:11px;color:#374151;background:#fef9ec;border:1px solid #fde68a;border-radius:6px;padding:6px 8px;line-height:1.5;">
        <span style="font-weight:600;">Recommended:</span> ${(c.recommended_action ?? '').slice(0, 80)}…
      </div>
    </div>`
}

// ── Leaflet Map component ─────────────────────────────────────
function LeafletMap({ clusters, mode }) {
  const mapRef      = useRef(null)
  const instanceRef = useRef(null)
  const heatRef     = useRef(null)
  const markersRef  = useRef([])

  useEffect(() => {
    if (!window.L || instanceRef.current) return
    const L   = window.L
    const map = L.map(mapRef.current, { center: [28.6139, 77.1500], zoom: 11 })
    instanceRef.current = map

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map)

    return () => { map.remove(); instanceRef.current = null }
  }, [])

  // Re-draw markers + heatmap whenever clusters data changes
  useEffect(() => {
    const map = instanceRef.current
    if (!map || !window.L) return
    const L = window.L

    // Clear old markers & heat layer
    markersRef.current.forEach((m) => map.removeLayer(m))
    markersRef.current = []
    if (heatRef.current) { map.removeLayer(heatRef.current); heatRef.current = null }

    const validClusters = clusters.filter((c) => c.lat && c.lng)

    // Markers
    const newMarkers = validClusters.map((c) =>
      L.marker([c.lat, c.lng], { icon: makeIcon(L, PRIORITY_COLORS[c.priority] ?? '#9ca3af') })
        .bindPopup(popupHTML(c), { maxWidth: 280 })
    )
    markersRef.current = newMarkers

    // Heatmap
    if (window.L.heatLayer) {
      const heatData = validClusters.map((c) => [c.lat, c.lng, Math.min(c.complaint_count / 200, 1.0)])
      heatRef.current = window.L.heatLayer(heatData, {
        radius: 50, blur: 35, maxZoom: 13, max: 1.0,
        gradient: { 0.3: '#6366f1', 0.6: '#f97316', 0.85: '#ef4444', 1.0: '#be123c' },
      })
    }

    // Apply mode
    applyMode(map, mode)
  }, [clusters]) // eslint-disable-line react-hooks/exhaustive-deps

  function applyMode(map, mode) {
    if (!map) return
    if (mode === 'heatmap') {
      markersRef.current.forEach((m) => map.removeLayer(m))
      if (heatRef.current) heatRef.current.addTo(map)
    } else if (mode === 'pins') {
      if (heatRef.current) map.removeLayer(heatRef.current)
      markersRef.current.forEach((m) => m.addTo(map))
    } else {
      markersRef.current.forEach((m) => m.addTo(map))
      if (heatRef.current) heatRef.current.addTo(map)
    }
  }

  // Mode toggle without re-building markers
  useEffect(() => {
    applyMode(instanceRef.current, mode)
  }, [mode]) // eslint-disable-line react-hooks/exhaustive-deps

  return <div ref={mapRef} className="w-full h-full rounded-xl overflow-hidden" />
}

// ── Main page ─────────────────────────────────────────────────
export default function Maps() {
  const [mode, setMode]           = useState('both')
  const [scriptsReady, setReady]  = useState(false)
  const [selectedId, setSelected] = useState(null)

  const { clusters, loading } = useClusters()

  // Load Leaflet + leaflet.heat from CDN
  useEffect(() => {
    if (window.L?.heatLayer) { setReady(true); return }
    const leafletCSS = document.createElement('link')
    leafletCSS.rel  = 'stylesheet'
    leafletCSS.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
    document.head.appendChild(leafletCSS)
    const loadScript = (src) => new Promise((res) => {
      const s = document.createElement('script')
      s.src = src; s.async = false; s.onload = res
      document.head.appendChild(s)
    })
    loadScript('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js')
      .then(() => loadScript('https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js'))
      .then(() => setReady(true))
  }, [])

  const sorted = [...clusters].sort((a, b) => b.complaint_count - a.complaint_count)

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-4">
        <div className="max-w-3xl">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
            Complaint Hotspot &amp; Density Map
          </h2>
          <p className="text-[13.5px] font-medium text-gray-500 dark:text-gray-400 mt-1.5 leading-relaxed">
            Interactive heatmap of {loading ? '…' : clusters.length} civic issue clusters across Delhi.{' '}
            <strong className="text-indigo-500 dark:text-indigo-400 font-semibold">Red areas</strong> indicate highest complaint density.
          </p>
        </div>

        {/* Mode toggle */}
        <div className="flex items-center gap-1 glass-panel rounded-lg p-1 self-start flex-shrink-0">
          {[
            { key: 'pins',    label: 'Pins',    icon: MapPin },
            { key: 'heatmap', label: 'Heatmap', icon: Layers },
            { key: 'both',    label: 'Both',    icon: TrendingUp },
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setMode(key)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium transition-colors
                ${mode === key
                  ? 'bg-white dark:bg-gray-600 text-gray-800 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                }`}
            >
              <Icon size={13} />{label}
            </button>
          ))}
        </div>
      </div>

      {/* Map + sidebar */}
      <div className="flex flex-col lg:flex-row gap-4">

        {/* Map */}
        <div className="flex-1 min-h-[320px] h-[45vw] lg:h-[520px] glass-panel rounded-xl overflow-hidden shadow-2xl relative z-0">
          {scriptsReady && !loading
            ? <LeafletMap clusters={clusters} mode={mode} />
            : (
              <div className="w-full h-full flex items-center justify-center">
                <p className="text-[13px] text-gray-400 animate-pulse">
                  {loading ? 'Loading clusters…' : 'Loading map…'}
                </p>
              </div>
            )
          }
        </div>

        {/* Sidebar list */}
        <div className="w-full lg:w-72 flex flex-col gap-3 glass-panel p-3 animate-fade-in-up">
          <div className="flex items-center gap-2 px-1 border-b border-gray-200/50 dark:border-gray-700/50 pb-2 mb-1">
            <List size={15} className="text-indigo-500" />
            <span className="text-[13px] font-semibold text-gray-700 dark:text-gray-200">
              Area-wise Critical Clusters
            </span>
          </div>

          <div className="flex flex-col gap-2 overflow-y-auto max-h-[400px] lg:max-h-[488px] pr-0.5">
            {loading
              ? Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-gray-200/50 dark:border-gray-700/50 p-3 animate-pulse space-y-2">
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
                    <div className="h-2 bg-gray-100 dark:bg-gray-700/50 rounded w-1/2" />
                  </div>
                ))
              : sorted.map((c, i) => {
                  const color      = PRIORITY_COLORS[c.priority] ?? '#9ca3af'
                  const isSelected = selectedId === c.cluster_id
                  return (
                    <button
                      key={c.cluster_id}
                      onClick={() => setSelected(isSelected ? null : c.cluster_id)}
                      className={`w-full text-left rounded-xl p-3 transition-all
                        ${isSelected
                          ? 'border border-indigo-400 bg-indigo-50/80 dark:bg-indigo-900/40 shadow-md'
                          : 'border border-gray-200/50 dark:border-gray-700/50 bg-white/50 dark:bg-gray-800/50 hover:bg-white/80 dark:hover:bg-gray-800/80'
                        }`}
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-[10px] font-bold w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5"
                          style={{ background: color + '20', color }}>
                          {i + 1}
                        </span>
                        <p className="text-[12px] font-medium text-gray-800 dark:text-gray-100 leading-snug flex-1">
                          {c.problem}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 mt-2 pl-7">
                        <span className="flex items-center gap-1 text-[11px] text-gray-400"><MapPin size={10} />{c.location.split(',')[0]}</span>
                        <span className="flex items-center gap-1 text-[11px] text-gray-400"><Building2 size={10} />{c.department}</span>
                      </div>
                      <div className="flex items-center justify-between mt-2 pl-7">
                        <span className="flex items-center gap-1 text-[11px] font-medium" style={{ color }}>
                          <AlertCircle size={10} />{c.complaint_count} complaints
                        </span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${STATUS_STYLES[c.status] ?? ''}`}>
                          {STATUS_LABELS[c.status] ?? c.status}
                        </span>
                      </div>
                      {isSelected && (
                        <div className="mt-3 pt-3 border-t border-indigo-200 dark:border-indigo-800 pl-7 space-y-1.5">
                          <p className="text-[11px] text-gray-500 dark:text-gray-400 leading-relaxed">{c.summary}</p>
                          <p className="text-[11px] text-indigo-600 dark:text-indigo-400 leading-relaxed">
                            <span className="font-medium">Action: </span>{c.recommended_action}
                          </p>
                          <div className="flex gap-3 pt-1">
                            <span className="text-[11px] text-gray-400">
                              RT reach: <span className="font-medium text-gray-700 dark:text-gray-200">{c.rt_reach?.toLocaleString()}</span>
                            </span>
                            <span className="text-[11px] text-gray-400">
                              Trend: <span className={`font-medium ${c.trend === 'up' ? 'text-red-500' : c.trend === 'down' ? 'text-green-600' : 'text-gray-500'}`}>
                                {c.trend === 'up' ? '↑ Rising' : c.trend === 'down' ? '↓ Falling' : '→ Stable'}
                              </span>
                            </span>
                          </div>
                        </div>
                      )}
                    </button>
                  )
                })
            }
          </div>
        </div>
      </div>
    </div>
  )
}
