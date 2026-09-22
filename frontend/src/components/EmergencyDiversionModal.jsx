import React, { useState } from 'react';
import { AlertOctagon, X, Navigation, Anchor, DollarSign, Clock, ShieldCheck, MapPin, CheckCircle, ArrowRight } from 'lucide-react';

export default function EmergencyDiversionModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const [vesselType, setVesselType] = useState('Supramax');
  const [emergencyType, setEmergencyType] = useState('engine_fault');
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);

  const emergencyOptions = [
    { id: 'engine_fault', label: 'Engine Fault / Mechanical Breakdown', desc: 'Main propulsion or generator failure at sea' },
    { id: 'storm_diversion', label: 'Storm / Cyclone Diversion Order', desc: 'VTS port authority ordered reroute away from cyclone' },
    { id: 'medical', label: 'Crew Medical Emergency', desc: 'Urgent medical evacuation required' },
    { id: 'port_closure', label: 'Destination Port Closure', desc: 'Port closed due to draft limitation or emergency' },
  ];

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/live/diversion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vessel_type: vesselType,
          current_lat: 13.8,
          current_lon: 84.5,
          emergency_type: emergencyType,
          original_destination: 'paradip',
          cargo_quantity_mt: 55000,
          speed_knots: emergencyType === 'engine_fault' ? 8.5 : 12.0,
          fuel_price_usd_mt: 620.0,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setPlan(data);
      }
    } catch (err) {
      console.error('Diversion evaluation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-3xl w-full border border-slate-200 shadow-2xl overflow-hidden my-6">
        {/* Modal Header */}
        <div className="bg-gradient-to-r from-red-600 via-rose-600 to-orange-600 px-6 py-4 flex items-center justify-between text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-white/20 backdrop-blur-xs">
              <AlertOctagon className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <h2 className="text-base font-black tracking-tight">Ship Distress & Emergency Diversion System</h2>
              <p className="text-xs text-white/80 font-medium">Automated Safe Harbor Route, Cost Impact & ETA Recalculation</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-all text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {/* Controls: Select Emergency & Vessel */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-black uppercase tracking-wider text-slate-700 block mb-1.5">
                Vessel in Distress
              </label>
              <select
                value={vesselType}
                onChange={(e) => setVesselType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-red-500"
              >
                <option value="Supramax">MV Ocean Crest (Supramax · 58,000 DWT)</option>
                <option value="Panamax">MV Horizon Pioneer (Panamax · 75,000 DWT)</option>
                <option value="Handysize">MV Bay Runner (Handysize · 35,000 DWT)</option>
                <option value="Capesize">MV Iron Giant (Capesize · 180,000 DWT)</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1">Current Position: 13.8° N, 84.5° E (Bay of Bengal)</p>
            </div>

            <div>
              <label className="text-xs font-black uppercase tracking-wider text-slate-700 block mb-1.5">
                Emergency Scenario
              </label>
              <select
                value={emergencyType}
                onChange={(e) => setEmergencyType(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-red-500"
              >
                {emergencyOptions.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-500 mt-1">
                {emergencyOptions.find((o) => o.id === emergencyType)?.desc}
              </p>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex justify-center">
            <button
              onClick={handleEvaluate}
              disabled={loading}
              className="px-6 py-2.5 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-red-500/25 transition-all flex items-center gap-2 active:scale-95 disabled:opacity-50"
            >
              <Navigation className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Calculating Nearest Safe Harbor...' : 'Calculate Safe Harbor & Extra Cost'}</span>
            </button>
          </div>

          {/* Results Section */}
          {plan && (
            <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
                  <h3 className="text-xs font-black uppercase tracking-wider text-slate-900">
                    Recommended Diversion: {plan.recommended_diversion_port.name}
                  </h3>
                </div>
                <span className="bg-red-100 text-red-700 text-[11px] font-black px-2.5 py-0.5 rounded-full border border-red-200">
                  {plan.emergency_label}
                </span>
              </div>

              {/* KPI Grid for Diversion */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                  <div className="text-[10px] uppercase font-bold text-slate-500">Distance to Port</div>
                  <div className="text-base font-black text-slate-900 mt-0.5 font-mono">
                    {plan.recommended_diversion_port.distance_nm} nm
                  </div>
                  <div className="text-[10px] text-slate-500">~{plan.recommended_diversion_port.eta_hours} hrs steaming</div>
                </div>

                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                  <div className="text-[10px] uppercase font-bold text-slate-500">Estimated Delay</div>
                  <div className="text-base font-black text-orange-600 mt-0.5 font-mono">
                    +{plan.cost_impact.additional_delay_hours} hrs
                  </div>
                  <div className="text-[10px] text-slate-500">Includes port wait & repair</div>
                </div>

                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                  <div className="text-[10px] uppercase font-bold text-slate-500">Extra Total Cost</div>
                  <div className="text-base font-black text-red-600 mt-0.5 font-mono">
                    ${plan.cost_impact.total_extra_cost_usd?.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-500">Fuel + Harbor Dues</div>
                </div>

                <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-2xs">
                  <div className="text-[10px] uppercase font-bold text-slate-500">Revised Final ETA</div>
                  <div className="text-xs font-black text-slate-800 mt-1">
                    {plan.cost_impact.revised_destination_eta}
                  </div>
                  <div className="text-[10px] text-slate-500">At Paradip Port</div>
                </div>
              </div>

              {/* Port Capabilities */}
              <div className="bg-white p-3.5 rounded-lg border border-slate-200 text-xs">
                <span className="font-bold text-slate-700 block mb-1">
                  Harbor Facilities at {plan.recommended_diversion_port.name}:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {plan.recommended_diversion_port.services_available?.map((srv, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded font-semibold text-[11px]"
                    >
                      ✓ {srv}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Protocol Checklist */}
              <div className="space-y-1.5 text-xs text-slate-700">
                <span className="font-black uppercase tracking-wider text-slate-900 block text-[11px]">
                  Emergency Protocol & Compliance Steps:
                </span>
                {plan.recommendations?.map((rec, i) => (
                  <div key={i} className="flex items-start gap-2 bg-white p-2 rounded border border-slate-100">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-100 px-6 py-3 border-t border-slate-200 flex justify-between items-center text-xs">
          <span className="text-slate-500 font-medium">All estimates based on live maritime geospatial models</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white font-bold rounded-lg transition-all"
          >
            Close Dialog
          </button>
        </div>
      </div>
    </div>
  );
}
