import React, { useState } from 'react';
import {
  Ship,
  CheckCircle2,
  AlertTriangle,
  Anchor,
  Compass,
  DollarSign,
  Calendar,
  Filter,
  ArrowRight,
  ShieldCheck,
  X,
  Gauge,
  Sliders
} from 'lucide-react';

export default function VesselMatchingView({ dashboardData, onSelectVessel }) {
  const [selectedClass, setSelectedClass] = useState('ALL');
  const [activeVessel, setActiveVessel] = useState(null);

  const defaultFleet = [
    {
      vessel_id: 'V0006',
      vessel_name: 'MV Ocean Crest',
      vessel_type: 'Supramax',
      dwt_mt: 58000,
      draft_m: 12.5,
      loa_m: 199.9,
      beam_m: 32.2,
      built_year: 2018,
      flag: 'Singapore',
      gear: '4x30T Cranes + Grabs',
      eta: '18 Sep 2026',
      match_score: 95,
      freight_rate_usd_mt: 9.90,
      total_cost_usd: 816127,
      cost_per_mt: 14.81,
      risk_level: 'LOW',
      feasible: true,
      port_compatibility: 'Paradip, Vizag, Gangavaram, Gopalpur',
      reasons: [
        'Complies with Paradip draft, LOA, and beam restrictions',
        'Self-discharging 4x30T cranes enable flexible berth allocation',
        'Optimal parcel capacity for 58,000 MT multi-voyage tranche',
      ],
    },
    {
      vessel_id: 'V0007',
      vessel_name: 'MV Eastern Star',
      vessel_type: 'Supramax',
      dwt_mt: 62000,
      draft_m: 12.8,
      loa_m: 200.0,
      beam_m: 32.2,
      built_year: 2020,
      flag: 'Marshall Islands',
      gear: '4x35T Cranes',
      eta: '21 Sep 2026',
      match_score: 95,
      freight_rate_usd_mt: 9.90,
      total_cost_usd: 853747,
      cost_per_mt: 14.49,
      risk_level: 'LOW',
      feasible: true,
      port_compatibility: 'Paradip, Vizag, Gangavaram',
      reasons: [
        'Modern eco-engine design with lower specific bunker consumption',
        'Full draft compliance across Bay of Bengal corridor',
        'High cargo intake (62,000 DWT) reduces unit freight $/MT',
      ],
    },
    {
      vessel_id: 'V0011',
      vessel_name: 'MV Horizon Pioneer',
      vessel_type: 'Panamax',
      dwt_mt: 75000,
      draft_m: 14.0,
      loa_m: 225.0,
      beam_m: 32.2,
      built_year: 2017,
      flag: 'Panama',
      gear: 'Gearless',
      eta: '20 Sep 2026',
      match_score: 93,
      freight_rate_usd_mt: 9.50,
      total_cost_usd: 994388,
      cost_per_mt: 13.96,
      risk_level: 'LOW',
      feasible: true,
      port_compatibility: 'Paradip (Berth 2/3), Gangavaram',
      reasons: [
        'Low freight rate ($9.50/MT) yields strong economies of scale',
        'Complies with Paradip 17m deep-water bulk berth',
        'Large parcel size reduces required total voyage count to 3.3',
      ],
    },
    {
      vessel_id: 'V0008',
      vessel_name: 'MV Pacific Trader',
      vessel_type: 'Supramax',
      dwt_mt: 55000,
      draft_m: 12.3,
      loa_m: 190.0,
      beam_m: 32.2,
      built_year: 2014,
      flag: 'Liberia',
      gear: '4x30T Cranes',
      eta: '25 Sep 2026',
      match_score: 88,
      freight_rate_usd_mt: 10.15,
      total_cost_usd: 840500,
      cost_per_mt: 15.28,
      risk_level: 'MEDIUM',
      feasible: true,
      port_compatibility: 'All East Coast Ports',
      reasons: [
        'Readily available prompt positioning near Singapore strait',
        'Standard Supramax workhorse with established track record',
      ],
    },
    {
      vessel_id: 'V0016',
      vessel_name: 'MV Iron Titan',
      vessel_type: 'Capesize',
      dwt_mt: 180000,
      draft_m: 18.2,
      loa_m: 292.0,
      beam_m: 45.0,
      built_year: 2019,
      flag: 'Singapore',
      gear: 'Gearless',
      eta: '28 Sep 2026',
      match_score: 72,
      freight_rate_usd_mt: 8.80,
      total_cost_usd: 1780000,
      cost_per_mt: 10.45,
      risk_level: 'HIGH',
      feasible: false,
      port_compatibility: 'Gangavaram Only (Exceeds Paradip max draft)',
      reasons: [
        'Lowest freight rate ($8.80/MT) but exceeds Paradip draft limits (18.2m > 17.0m)',
        'Requires offshore lightering or diversion to deep-water Gangavaram',
      ],
    },
    {
      vessel_id: 'V0002',
      vessel_name: 'MV Bengal Carrier',
      vessel_type: 'Handysize',
      dwt_mt: 34000,
      draft_m: 10.1,
      loa_m: 177.0,
      beam_m: 28.0,
      built_year: 2016,
      flag: 'India',
      gear: '4x25T Cranes',
      eta: '17 Sep 2026',
      match_score: 79,
      freight_rate_usd_mt: 11.20,
      total_cost_usd: 542000,
      cost_per_mt: 16.90,
      risk_level: 'LOW',
      feasible: true,
      port_compatibility: 'All Ports (including shallow Haldia)',
      reasons: [
        'Shallow draft allows unrestricted entry into all East Coast berths',
        'Higher unit freight ($11.20/MT) makes it suboptimal for large 250k MT volume',
      ],
    },
  ];

  const filtered = selectedClass === 'ALL'
    ? defaultFleet
    : defaultFleet.filter((v) => v.vessel_type.toUpperCase() === selectedClass);

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Fleet Matching Engine
              </span>
              <span className="text-xs text-slate-400">Target Cargo: 250,000 MT Iron Ore | Balikpapan → Paradip</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <Ship className="w-6 h-6 text-blue-400" />
              Vessel Selection & Match Optimization
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Automated multi-criteria ranking based on port physical constraints (draft, LOA, beam), total voyage economics, carbon-efficient eco-speeds, and prompt loading window availability.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {['ALL', 'SUPRAMAX', 'PANAMAX', 'CAPESIZE', 'HANDYSIZE'].map((cls) => (
              <button
                key={cls}
                onClick={() => setSelectedClass(cls)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  selectedClass === cls
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white'
                }`}
              >
                {cls}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Candidates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((v) => {
          const isTop = v.match_score >= 95;
          return (
            <div
              key={v.vessel_id}
              className={`bg-white rounded-2xl p-5 border transition-all flex flex-col justify-between ${
                isTop
                  ? 'border-blue-300 shadow-md shadow-blue-500/10 ring-1 ring-blue-200'
                  : 'border-slate-200 shadow-sm hover:border-slate-300'
              }`}
            >
              <div>
                {/* Card Top */}
                <div className="flex items-start justify-between gap-2 border-b border-slate-100 pb-3 mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-black text-slate-900 text-base">{v.vessel_name}</h3>
                      {isTop && (
                        <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-blue-100 text-blue-700">
                          Top Choice
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500">{v.vessel_type} • {v.dwt_mt.toLocaleString()} DWT • Built {v.built_year}</p>
                  </div>

                  <div className="text-right">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black bg-blue-600 text-white">
                      {v.match_score}%
                    </span>
                    <p className="text-[10px] text-slate-400 mt-0.5">Fit Score</p>
                  </div>
                </div>

                {/* Specs Pill List */}
                <div className="grid grid-cols-3 gap-2 text-center text-xs mb-3">
                  <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                    <p className="text-[10px] text-slate-400 uppercase font-bold">Max Draft</p>
                    <p className="font-bold text-slate-800">{v.draft_m}m</p>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                    <p className="text-[10px] text-slate-400 uppercase font-bold">Length (LOA)</p>
                    <p className="font-bold text-slate-800">{v.loa_m}m</p>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-lg border border-slate-100">
                    <p className="text-[10px] text-slate-400 uppercase font-bold">Beam</p>
                    <p className="font-bold text-slate-800">{v.beam_m}m</p>
                  </div>
                </div>

                {/* Pricing & Cost */}
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1.5 text-xs mb-3">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Freight Rate:</span>
                    <span className="font-bold text-slate-900">${v.freight_rate_usd_mt.toFixed(2)} / MT</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Single Voyage Cost:</span>
                    <span className="font-bold text-slate-900">${(v.total_cost_usd / 1000).toFixed(0)}k</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Landed Cost / MT:</span>
                    <span className="font-bold text-blue-600">${v.cost_per_mt.toFixed(2)} / MT</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Port Feasibility:</span>
                    <span className={`font-bold ${v.feasible ? 'text-emerald-600' : 'text-red-600'}`}>
                      {v.feasible ? '✓ Feasible at Paradip' : '✗ Exceeds Draft Limit'}
                    </span>
                  </div>
                </div>

                {/* Bullet Reasons */}
                <div className="text-[11px] text-slate-600 space-y-1 mb-4">
                  {v.reasons.map((r, i) => (
                    <p key={i} className="flex items-start gap-1.5">
                      <span className="text-blue-500 font-bold">•</span>
                      <span>{r}</span>
                    </p>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                <button
                  onClick={() => setActiveVessel(v)}
                  className="flex-1 py-2 rounded-lg text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-all text-center"
                >
                  Inspect Vessel
                </button>
                <button
                  onClick={() => onSelectVessel ? onSelectVessel(v) : setActiveVessel(v)}
                  className="flex-1 py-2 rounded-lg text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white transition-all text-center shadow-sm"
                >
                  Select for Charter
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal Inspector */}
      {activeVessel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Ship className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-slate-900 text-lg">{activeVessel.vessel_name}</h3>
                  <p className="text-xs text-slate-500">{activeVessel.vessel_type} • ID: {activeVessel.vessel_id}</p>
                </div>
              </div>
              <button
                onClick={() => setActiveVessel(null)}
                className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-500">Deadweight:</span>
                <p className="text-sm font-bold text-slate-900">{activeVessel.dwt_mt.toLocaleString()} MT</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-500">Handling Gear:</span>
                <p className="text-sm font-bold text-slate-900">{activeVessel.gear}</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-500">Draft Clearance @ Paradip:</span>
                <p className="text-sm font-bold text-emerald-600">+4.5m Clearance (Safe)</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-slate-500">Estimated Transit Time:</span>
                <p className="text-sm font-bold text-slate-900">7.2 Days @ 14.0 Knots</p>
              </div>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs space-y-1">
              <p className="font-bold text-blue-900">Port Compatibility Verdict:</p>
              <p className="text-blue-800">{activeVessel.port_compatibility}</p>
            </div>

            <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
              <button
                onClick={() => setActiveVessel(null)}
                className="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Close
              </button>
              <button
                onClick={() => {
                  if (onSelectVessel) onSelectVessel(activeVessel);
                  setActiveVessel(null);
                }}
                className="px-5 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-sm"
              >
                Proceed with Charter Party
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
