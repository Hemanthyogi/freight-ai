import React, { useState } from 'react';
import { AlertTriangle, Wind, Compass, X, ChevronDown, ChevronUp, ShieldAlert, Sparkles } from 'lucide-react';

export default function WeatherAlertBanner({ alerts, onLockCharter, onViewOperations }) {
  const [collapsed, setCollapsed] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !alerts || alerts.length === 0) return null;

  // Primary alert (first or highest severity)
  const primaryAlert = alerts[0];
  const severityColors = {
    CRITICAL: 'from-rose-900/90 to-red-800/90 border-rose-500 text-rose-100',
    HIGH: 'from-orange-900/90 to-amber-800/90 border-orange-500 text-orange-100',
    MEDIUM: 'from-amber-900/80 to-yellow-800/80 border-amber-500 text-amber-100',
    LOW: 'from-blue-900/70 to-indigo-900/70 border-blue-500 text-blue-100',
  }[primaryAlert.severity] || 'from-slate-800 to-slate-900 border-slate-600 text-slate-200';

  return (
    <div
      className={`rounded-xl border bg-gradient-to-r ${severityColors} p-3.5 shadow-lg backdrop-blur-sm transition-all relative overflow-hidden`}
    >
      {/* Background nautical pattern overlay */}
      <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-4">
        <Wind className="w-32 h-32" />
      </div>

      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        {/* Left: Icon & Alert Heading */}
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-black/20 shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5 text-amber-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-black uppercase tracking-wider px-2 py-0.5 rounded bg-black/30 border border-white/20">
                {primaryAlert.type} ALERT
              </span>
              <h3 className="text-sm font-extrabold text-white flex items-center gap-1.5">
                {primaryAlert.name}
              </h3>
              {primaryAlert.rate_impact_pct > 0 && (
                <span className="bg-rose-500/30 text-rose-200 text-xs font-bold px-2 py-0.5 rounded-full border border-rose-400/40">
                  +{primaryAlert.rate_impact_pct}% Projected Rate Surge
                </span>
              )}
            </div>

            {!collapsed && (
              <p className="text-xs mt-1 text-slate-100 font-medium leading-relaxed max-w-3xl">
                {primaryAlert.message}
              </p>
            )}

            {!collapsed && primaryAlert.wind_speed_kmh && (
              <div className="flex items-center gap-4 mt-2 text-[11px] text-slate-200 font-semibold">
                <span className="flex items-center gap-1">
                  <Wind className="w-3.5 h-3.5 text-amber-300" />
                  Winds: <strong className="text-white">{primaryAlert.wind_speed_kmh} km/h</strong>
                </span>
                {primaryAlert.distance_from_paradip_km && (
                  <span className="flex items-center gap-1">
                    <Compass className="w-3.5 h-3.5 text-blue-300" />
                    Distance: <strong className="text-white">{primaryAlert.distance_from_paradip_km} km to Paradip</strong>
                  </span>
                )}
                {primaryAlert.expected_landfall_hours && (
                  <span className="bg-white/10 px-2 py-0.5 rounded text-white">
                    Estimated Landfall: ~{primaryAlert.expected_landfall_hours} hrs
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 self-end md:self-center shrink-0">
          {onLockCharter && (
            <button
              onClick={onLockCharter}
              className="px-3.5 py-1.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-extrabold text-xs rounded-lg shadow-md transition-all flex items-center gap-1.5 active:scale-95"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Lock Charter Rate
            </button>
          )}

          {onViewOperations && (
            <button
              onClick={onViewOperations}
              className="px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white font-bold text-xs rounded-lg transition-all"
            >
              Live Radar
            </button>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 hover:bg-white/20 text-slate-300 hover:text-white rounded-lg transition-all"
            title={collapsed ? 'Expand alert' : 'Collapse alert'}
          >
            {collapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setDismissed(true)}
            className="p-1.5 hover:bg-white/20 text-slate-300 hover:text-white rounded-lg transition-all"
            title="Dismiss banner"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
