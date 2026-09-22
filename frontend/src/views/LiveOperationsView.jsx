import React, { useState } from 'react';
import {
  Radio,
  CloudLightning,
  AlertOctagon,
  Anchor,
  DollarSign,
  Sparkles,
  RefreshCw,
  Wind,
  Compass,
  Activity,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import AISuggestionsPanel from '../components/AISuggestionsPanel';
import LiveCostTracker from '../components/LiveCostTracker';
import EmergencyDiversionModal from '../components/EmergencyDiversionModal';
import WeatherAlertBanner from '../components/WeatherAlertBanner';

export default function LiveOperationsView({ liveData, onRefresh, loading }) {
  const [showEmergencyModal, setShowEmergencyModal] = useState(false);

  const bdi = liveData?.freight_rates?.bdi || 1842;
  const bdiChange = liveData?.freight_rates?.bdi_change_pct || 0;
  const weatherSeverity = liveData?.weather_severity || 'LOW';
  const weatherAdj = liveData?.freight_rates?.weather_adjustment_pct || 0;
  const portStatus = liveData?.port_status || {};
  const weatherAlerts = liveData?.weather_alerts || [];
  const suggestions = liveData?.ai_suggestions || [];

  return (
    <div className="space-y-5">
      {/* View Header */}
      <div className="bg-gradient-to-r from-[#0b1b36] via-[#102a54] to-[#153468] rounded-2xl p-6 text-white shadow-lg border border-[#1e427d] relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-[11px] font-black uppercase tracking-widest text-emerald-400">
                24/7 Live Maritime Intelligence
              </span>
              <span className="bg-blue-500/20 text-blue-300 text-[10px] font-bold px-2 py-0.5 rounded border border-blue-400/30">
                Auto-Sync 15m
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white">
              Live Voyage Operations & Climate Risk Center
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl font-medium leading-relaxed">
              Real-time monitoring of Bay of Bengal weather systems, dynamic freight rate drift, 
              proactive AI charter suggestions, and instant ship emergency diversion protocols.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowEmergencyModal(true)}
              className="px-4 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-red-600/30 transition-all flex items-center gap-2 active:scale-95 border border-red-400/40"
            >
              <AlertOctagon className="w-4 h-4" />
              <span>Simulate Ship Emergency</span>
            </button>

            <button
              onClick={onRefresh}
              disabled={loading}
              className="p-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-all border border-white/20"
              title="Refresh live feeds"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Weather Alert Banner */}
      <WeatherAlertBanner
        alerts={weatherAlerts}
        onLockCharter={() => {}}
        onViewOperations={() => {}}
      />

      {/* Main Grid: AI Suggestions & Live Cost Calculator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Left Column: Proactive AI Suggestions */}
        <AISuggestionsPanel
          suggestions={suggestions}
          onAction={(action) => {
            if (action === 'open_diversion') setShowEmergencyModal(true);
          }}
          onRefresh={onRefresh}
        />

        {/* Right Column: Live Renting vs Booking Cost Tracker */}
        <LiveCostTracker liveData={liveData} onBookNow={() => {}} />
      </div>

      {/* East Coast India Live Port Operational Status Board */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-slate-900 text-white">
              <Anchor className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-900">
                East Coast India — Live Port Congestion & Draft Feasibility
              </h3>
              <p className="text-[11px] text-slate-500 font-medium">
                Live vessel queue status, average anchorage wait times, and maximum permissible drafts
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
          {Object.entries(portStatus).map(([portId, pData]) => {
            const isCongested = pData.congestion === 'HIGH';
            const isRestricted = pData.status === 'RESTRICTED' || pData.status === 'CLOSED';

            return (
              <div
                key={portId}
                className={`p-3.5 rounded-xl border transition-all ${
                  isRestricted
                    ? 'bg-rose-50/50 border-rose-300'
                    : isCongested
                    ? 'bg-amber-50/50 border-amber-300'
                    : 'bg-slate-50/60 border-slate-200'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-black text-slate-900 capitalize">{portId}</span>
                  <span
                    className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                      isRestricted
                        ? 'bg-rose-100 text-rose-700'
                        : isCongested
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-emerald-100 text-emerald-700'
                    }`}
                  >
                    {pData.status}
                  </span>
                </div>

                <div className="space-y-1 text-xs text-slate-600 mt-2">
                  <div className="flex justify-between">
                    <span className="text-[11px] text-slate-500 font-medium">Congestion:</span>
                    <strong className="text-slate-800 font-mono">{pData.congestion}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[11px] text-slate-500 font-medium">Est. Wait:</span>
                    <strong className="text-slate-900 font-mono">{pData.waiting_hours} hrs</strong>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Emergency Diversion Modal */}
      <EmergencyDiversionModal
        isOpen={showEmergencyModal}
        onClose={() => setShowEmergencyModal(false)}
      />
    </div>
  );
}
