import React, { useState } from 'react';
import {
  Anchor,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  Layers,
  MapPin,
  Clock,
  Waves,
  ShieldCheck,
  Building,
  RefreshCw
} from 'lucide-react';

export default function PortFeasibilityView() {
  const [selectedPortId, setSelectedPortId] = useState('paradip');
  const [selectedVesselType, setSelectedVesselType] = useState('Supramax');
  const [cargoQty, setCargoQty] = useState(55000);

  const ports = [
    {
      id: 'paradip',
      name: 'Paradip Port',
      state: 'Odisha',
      max_draft: 17.0,
      max_loa: 300.0,
      max_beam: 45.0,
      avg_wait_hours: 40.4,
      berths: 16,
      mechanized: true,
      tidal_range: 2.8,
      notes: 'Deep-water mechanized bulk terminal; ideal for Supramax and Panamax iron ore/coal carriers.',
    },
    {
      id: 'visakhapatnam',
      name: 'Visakhapatnam Port',
      state: 'Andhra Pradesh',
      max_draft: 16.5,
      max_loa: 280.0,
      max_beam: 42.0,
      avg_wait_hours: 32.1,
      berths: 24,
      mechanized: true,
      tidal_range: 1.8,
      notes: 'Outer harbour accommodates deep-draft bulk carriers up to 150k DWT. Excellent rail connectivity.',
    },
    {
      id: 'haldia',
      name: 'Haldia Dock Complex',
      state: 'West Bengal',
      max_draft: 9.5,
      max_loa: 230.0,
      max_beam: 32.2,
      avg_wait_hours: 78.1,
      berths: 14,
      mechanized: true,
      tidal_range: 4.2,
      notes: 'High congestion risk (78.1h avg wait). Strict 9.5m river draft restriction; Capesize/Panamax strictly prohibited.',
    },
    {
      id: 'gangavaram',
      name: 'Gangavaram Port',
      state: 'Andhra Pradesh',
      max_draft: 21.0,
      max_loa: 340.0,
      max_beam: 55.0,
      avg_wait_hours: 16.3,
      berths: 9,
      mechanized: true,
      tidal_range: 1.6,
      notes: 'Deepest port in India (21m draft). Can handle fully laden Capesize bulk carriers with minimal waiting time.',
    },
    {
      id: 'gopalpur',
      name: 'Gopalpur Port',
      state: 'Odisha',
      max_draft: 14.5,
      max_loa: 240.0,
      max_beam: 36.0,
      avg_wait_hours: 15.6,
      berths: 4,
      mechanized: true,
      tidal_range: 2.2,
      notes: 'Fast turnaround, lowest congestion (15.6h avg wait). Suitable for Handysize and Supramax vessels.',
    },
    {
      id: 'dhamra',
      name: 'Dhamra Port',
      state: 'Odisha',
      max_draft: 18.0,
      max_loa: 315.0,
      max_beam: 48.0,
      avg_wait_hours: 24.5,
      berths: 5,
      mechanized: true,
      tidal_range: 3.5,
      notes: 'Modern private deep-water bulk port. Capable of handling Capesize vessels with high discharge rates.',
    },
    {
      id: 'sagar_sandheads',
      name: 'Sagar Sandheads (Lighterage)',
      state: 'West Bengal',
      max_draft: 15.0,
      max_loa: 275.0,
      max_beam: 40.0,
      avg_wait_hours: 48.0,
      berths: 2,
      mechanized: false,
      tidal_range: 4.8,
      notes: 'Offshore anchorage used for transshipment and lighterage before entering shallow Hooghly river.',
    },
  ];

  const vessels = {
    Handysize: { draft: 10.5, loa: 180.0, beam: 28.5, capacity: 35000, typical_dwt: '28,000 - 39,000 DWT' },
    Supramax: { draft: 12.5, loa: 200.0, beam: 32.2, capacity: 58000, typical_dwt: '50,000 - 64,000 DWT' },
    Panamax: { draft: 14.0, loa: 225.0, beam: 32.2, capacity: 75000, typical_dwt: '65,000 - 82,000 DWT' },
    Capesize: { draft: 18.2, loa: 295.0, beam: 45.0, capacity: 180000, typical_dwt: '120,000 - 200,000 DWT' },
  };

  const currentPort = ports.find((p) => p.id === selectedPortId) || ports[0];
  const currentVessel = vessels[selectedVesselType];

  // Constraint Checks
  const draftPassed = currentVessel.draft <= currentPort.max_draft;
  const loaPassed = currentVessel.loa <= currentPort.max_loa;
  const beamPassed = currentVessel.beam <= currentPort.max_beam;
  const capacityPassed = cargoQty <= currentVessel.capacity;
  const isOverallFeasible = draftPassed && loaPassed && beamPassed;

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Maritime Hydrographic Engine
              </span>
              <span className="text-xs text-slate-400">7 East Coast Major Ports & Deepwater Terminals</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <Anchor className="w-6 h-6 text-blue-400" />
              Port Feasibility & Hard-Constraint Checker
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Validates vessel physical dimensions against port max draft, LOA, beam, and tidal fluctuations to prevent costly lightering delays, demurrage, or port rejections.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wider flex items-center gap-2 ${
              isOverallFeasible
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30'
                : 'bg-red-500/20 text-red-300 border border-red-400/30'
            }`}>
              {isOverallFeasible ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  BERTHING FEASIBLE
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 text-red-400" />
                  CONSTRAINT VIOLATION
                </>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
            Select Destination Port:
          </label>
          <select
            value={selectedPortId}
            onChange={(e) => setSelectedPortId(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {ports.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.state}) — Draft: {p.max_draft}m
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
            Select Vessel Class:
          </label>
          <select
            value={selectedVesselType}
            onChange={(e) => setSelectedVesselType(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {Object.keys(vessels).map((vKey) => (
              <option key={vKey} value={vKey}>
                {vKey} ({vessels[vKey].typical_dwt})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
            Parcel Quantity: {cargoQty.toLocaleString()} MT
          </label>
          <input
            type="range"
            min="20000"
            max="180000"
            step="5000"
            value={cargoQty}
            onChange={(e) => setCargoQty(Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </div>
      </div>

      {/* 4 Clearance Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Draft Check */}
        <div className={`bg-white rounded-2xl p-5 border shadow-sm ${
          draftPassed ? 'border-emerald-200' : 'border-red-300 ring-2 ring-red-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-600 uppercase">Draft Clearance</span>
            {draftPassed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="text-2xl font-black text-slate-900">{currentVessel.draft}m</span>
            <span className="text-xs text-slate-500">/ max {currentPort.max_draft}m</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 mb-2 overflow-hidden">
            <div
              className={`h-full rounded-full ${draftPassed ? 'bg-emerald-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(100, (currentVessel.draft / currentPort.max_draft) * 100)}%` }}
            ></div>
          </div>
          <p className="text-[11px] text-slate-500">
            {draftPassed
              ? `Safe clearance: +${(currentPort.max_draft - currentVessel.draft).toFixed(1)}m underkeel`
              : `Draft exceeded by ${(currentVessel.draft - currentPort.max_draft).toFixed(1)}m — ground risk`}
          </p>
        </div>

        {/* LOA Check */}
        <div className={`bg-white rounded-2xl p-5 border shadow-sm ${
          loaPassed ? 'border-emerald-200' : 'border-red-300 ring-2 ring-red-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-600 uppercase">Length Overall (LOA)</span>
            {loaPassed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="text-2xl font-black text-slate-900">{currentVessel.loa}m</span>
            <span className="text-xs text-slate-500">/ max {currentPort.max_loa}m</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 mb-2 overflow-hidden">
            <div
              className={`h-full rounded-full ${loaPassed ? 'bg-emerald-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(100, (currentVessel.loa / currentPort.max_loa) * 100)}%` }}
            ></div>
          </div>
          <p className="text-[11px] text-slate-500">
            {loaPassed ? 'Within quay berth envelope' : 'Vessel exceeds maximum berth length'}
          </p>
        </div>

        {/* Beam Check */}
        <div className={`bg-white rounded-2xl p-5 border shadow-sm ${
          beamPassed ? 'border-emerald-200' : 'border-red-300 ring-2 ring-red-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-600 uppercase">Beam Width</span>
            {beamPassed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="text-2xl font-black text-slate-900">{currentVessel.beam}m</span>
            <span className="text-xs text-slate-500">/ max {currentPort.max_beam}m</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 mb-2 overflow-hidden">
            <div
              className={`h-full rounded-full ${beamPassed ? 'bg-emerald-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(100, (currentVessel.beam / currentPort.max_beam) * 100)}%` }}
            ></div>
          </div>
          <p className="text-[11px] text-slate-500">
            {beamPassed ? 'Complies with channel entrance width' : 'Exceeds channel navigational envelope'}
          </p>
        </div>

        {/* Parcel Capacity Check */}
        <div className={`bg-white rounded-2xl p-5 border shadow-sm ${
          capacityPassed ? 'border-emerald-200' : 'border-amber-300'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-600 uppercase">Parcel Capacity</span>
            {capacityPassed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-amber-600" />
            )}
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="text-2xl font-black text-slate-900">{(cargoQty / 1000).toFixed(0)}k MT</span>
            <span className="text-xs text-slate-500">/ cap {(currentVessel.capacity / 1000).toFixed(0)}k MT</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 mb-2 overflow-hidden">
            <div
              className={`h-full rounded-full ${capacityPassed ? 'bg-emerald-500' : 'bg-amber-500'}`}
              style={{ width: `${Math.min(100, (cargoQty / currentVessel.capacity) * 100)}%` }}
            ></div>
          </div>
          <p className="text-[11px] text-slate-500">
            {capacityPassed
              ? `Load factor: ${((cargoQty / currentVessel.capacity) * 100).toFixed(0)}% (Optimal)`
              : `Over-capacity: requires multiple sequenced voyages`}
          </p>
        </div>
      </div>

      {/* Port Operational Profile */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <Building className="w-4 h-4 text-blue-600" />
          <h3 className="text-sm font-black text-slate-900">
            {currentPort.name} Operational Profile & Hydrographic Conditions
          </h3>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 uppercase font-bold text-[10px]">Average Waiting Time</span>
            <p className="text-base font-black text-slate-900 mt-0.5">{currentPort.avg_wait_hours} hrs</p>
            <p className="text-[10px] text-slate-500">Queuing delay buffer</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 uppercase font-bold text-[10px]">Tidal Range</span>
            <p className="text-base font-black text-slate-900 mt-0.5">±{currentPort.tidal_range} m</p>
            <p className="text-[10px] text-slate-500">Semi-diurnal tide cycle</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 uppercase font-bold text-[10px]">Active Berths</span>
            <p className="text-base font-black text-slate-900 mt-0.5">{currentPort.berths} Berths</p>
            <p className="text-[10px] text-slate-500">{currentPort.mechanized ? 'Mechanized Conveyors' : 'Grab Cranes'}</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
            <span className="text-slate-400 uppercase font-bold text-[10px]">Congestion Risk Level</span>
            <p className={`text-base font-black mt-0.5 ${
              currentPort.avg_wait_hours > 50 ? 'text-red-600' : currentPort.avg_wait_hours > 25 ? 'text-amber-600' : 'text-emerald-600'
            }`}>
              {currentPort.avg_wait_hours > 50 ? 'HIGH' : currentPort.avg_wait_hours > 25 ? 'MEDIUM' : 'LOW'}
            </p>
            <p className="text-[10px] text-slate-500">Historical seasonal average</p>
          </div>
        </div>

        <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Port Pilotage & Berthing Advisory: </span>
            <span>{currentPort.notes}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
