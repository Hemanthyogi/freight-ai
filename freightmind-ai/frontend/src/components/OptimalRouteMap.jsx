import React, { useState } from 'react';
import { MapPin, Navigation, Clock, Anchor, CloudSun } from 'lucide-react';

export default function OptimalRouteMap({ routeData }) {
  const [activePort, setActivePort] = useState(null);

  const data = routeData || {
    distance_nm: 2450,
    estimated_transit_days: 7.2,
    port_congestion: 'LOW',
    weather_risk: 'LOW',
    origin: { name: 'Indonesia (Balikpapan)' },
    destination: { name: 'East Coast India (Paradip)' },
  };

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
      {/* Title */}
      <div className="flex items-center gap-2 mb-3">
        <MapPin className="w-5 h-5 text-blue-600" />
        <h2 className="text-xs font-black uppercase tracking-wider text-slate-800">
          OPTIMAL VOYAGE ROUTE
        </h2>
      </div>

      {/* Map & Telemetry Split */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Interactive Maritime SVG Map (2 cols) */}
        <div className="md:col-span-2 relative bg-[#e2ecf7] rounded-xl overflow-hidden border border-slate-200 h-48 flex items-center justify-center">
          <svg viewBox="0 0 500 240" className="w-full h-full">
            {/* Ocean background */}
            <rect width="500" height="240" fill="#d9e8f5" />

            {/* India Subcontinent Outline (Simplified Vector) */}
            <path
              d="M 60,10 L 130,10 L 160,50 L 155,100 L 135,160 L 110,210 L 95,210 L 80,160 L 60,120 Z"
              fill="#c8dbbe"
              stroke="#a8c49d"
              strokeWidth="1.5"
            />
            <text x="100" y="70" fontSize="11" fontWeight="bold" fill="#475569">INDIA</text>

            {/* Southeast Asia / Indonesia Landmass */}
            <path
              d="M 330,130 Q 360,150 400,165 Q 430,175 480,180 L 480,230 L 330,230 Z"
              fill="#c8dbbe"
              stroke="#a8c49d"
              strokeWidth="1.5"
            />
            <text x="380" y="200" fontSize="11" fontWeight="bold" fill="#475569">INDONESIA</text>

            {/* Bay of Bengal label */}
            <text x="210" y="110" fontSize="9" fontWeight="600" fill="#94a3b8" letterSpacing="1">
              Bay of Bengal
            </text>
            <text x="120" y="225" fontSize="8" fontWeight="600" fill="#94a3b8">
              Indian Ocean
            </text>

            {/* Shipping Corridor Trajectory Curve */}
            <path
              d="M 370,175 Q 260,195 180,140 Q 155,110 148,80"
              fill="none"
              stroke="#059669"
              strokeWidth="3"
              strokeDasharray="6 4"
            />

            {/* Animated Ship Marker along route */}
            <circle cx="260" cy="165" r="4" fill="#10b981">
              <animate attributeName="r" values="3;6;3" dur="2s" repeatCount="indefinite" />
            </circle>

            {/* East Coast Indian Ports */}
            {/* Paradip (Destination) */}
            <g
              className="cursor-pointer"
              onMouseEnter={() => setActivePort('Paradip')}
              onMouseLeave={() => setActivePort(null)}
            >
              <circle cx="148" cy="80" r="5" fill="#2563eb" stroke="#ffffff" strokeWidth="2" />
              <text x="156" y="83" fontSize="9" fontWeight="bold" fill="#0f172a">Paradip</text>
            </g>

            {/* Visakhapatnam */}
            <g
              className="cursor-pointer"
              onMouseEnter={() => setActivePort('Vizag')}
              onMouseLeave={() => setActivePort(null)}
            >
              <circle cx="142" cy="110" r="4" fill="#3b82f6" stroke="#ffffff" strokeWidth="1.5" />
              <text x="150" y="113" fontSize="8" fontWeight="600" fill="#334155">Visakhapatnam</text>
            </g>

            {/* Chennai */}
            <g
              className="cursor-pointer"
              onMouseEnter={() => setActivePort('Chennai')}
              onMouseLeave={() => setActivePort(null)}
            >
              <circle cx="130" cy="150" r="4" fill="#64748b" stroke="#ffffff" strokeWidth="1.5" />
              <text x="138" y="153" fontSize="8" fontWeight="600" fill="#334155">Chennai</text>
            </g>

            {/* Origin Marker (Balikpapan / Indonesia) */}
            <g>
              <circle cx="370" cy="175" r="6" fill="#f59e0b" stroke="#ffffff" strokeWidth="2" />
              <text x="380" y="178" fontSize="9" fontWeight="bold" fill="#78350f">
                Indonesia (Origin)
              </text>
            </g>

            {/* Destination Pill Flag */}
            <g transform="translate(90, 95)">
              <rect width="85" height="18" rx="4" fill="#ffffff" fillOpacity="0.9" stroke="#10b981" strokeWidth="1" />
              <text x="6" y="12" fontSize="8" fontWeight="bold" fill="#065f46">
                East Coast India
              </text>
            </g>
          </svg>
        </div>

        {/* Route Telemetry Column (1 col) */}
        <div className="flex flex-col justify-between space-y-2">
          {/* Distance */}
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Navigation className="w-4 h-4 text-blue-600" />
              <div>
                <div className="text-[9px] font-bold uppercase text-slate-400">VOYAGE DISTANCE</div>
                <div className="text-sm font-black text-slate-900">{data.distance_nm.toLocaleString()} NM</div>
              </div>
            </div>
          </div>

          {/* Transit Time */}
          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-600" />
              <div>
                <div className="text-[9px] font-bold uppercase text-slate-400">ESTIMATED TRANSIT</div>
                <div className="text-sm font-black text-slate-900">{data.estimated_transit_days} Days</div>
              </div>
            </div>
          </div>

          {/* Port Congestion */}
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Anchor className="w-4 h-4 text-emerald-600" />
              <div>
                <div className="text-[9px] font-bold uppercase text-emerald-700">PORT CONGESTION</div>
                <div className="text-xs font-black text-emerald-800">{data.port_congestion}</div>
              </div>
            </div>
          </div>

          {/* Weather Risk */}
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CloudSun className="w-4 h-4 text-emerald-600" />
              <div>
                <div className="text-[9px] font-bold uppercase text-emerald-700">WEATHER RISK</div>
                <div className="text-xs font-black text-emerald-800">{data.weather_risk}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
