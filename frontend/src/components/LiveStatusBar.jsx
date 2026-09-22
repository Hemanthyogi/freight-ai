import React from 'react';
import { Activity, CloudLightning, RefreshCw, Radio, TrendingUp, TrendingDown, Anchor } from 'lucide-react';

export default function LiveStatusBar({ liveData, onRefresh, loading }) {
  if (!liveData) return null;

  const bdi = liveData.freight_rates?.bdi || 1842;
  const bdiChange = liveData.freight_rates?.bdi_change_pct || 0;
  const weatherSeverity = liveData.weather_severity || 'LOW';
  const weatherAlertsCount = liveData.weather_alerts?.length || 0;
  const weatherAdj = liveData.freight_rates?.weather_adjustment_pct || 0;

  const severityBadgeClass = {
    LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    MEDIUM: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    CRITICAL: 'bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse',
  }[weatherSeverity] || 'bg-slate-500/10 text-slate-400 border-slate-500/20';

  const formattedTime = liveData.last_updated
    ? new Date(liveData.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    : 'Live';

  return (
    <div className="bg-[#0b1b36] border-b border-[#1c355e] text-white px-5 py-2 flex flex-wrap items-center justify-between gap-3 text-xs shadow-inner">
      {/* Left: 24/7 Live Stream indicator */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-300 flex items-center gap-1">
            <Radio className="w-3 h-3" />
            24/7 Live Stream
          </span>
        </div>

        <span className="text-slate-400 text-[11px] hidden sm:inline">
          Sync: <strong className="text-slate-200 font-mono">{formattedTime}</strong>
        </span>
      </div>

      {/* Middle: Live Market & Weather Tickers */}
      <div className="flex items-center gap-4 flex-wrap">
        {/* Baltic Dry Index (BDI) */}
        <div className="flex items-center gap-1.5 bg-[#12284d] px-2.5 py-1 rounded-lg border border-[#203f73]">
          <Activity className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-slate-300 font-semibold text-[11px]">BDI:</span>
          <span className="font-bold text-white font-mono">{bdi.toLocaleString()}</span>
          <span
            className={`flex items-center text-[10px] font-bold ${
              bdiChange >= 0 ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {bdiChange >= 0 ? <TrendingUp className="w-2.5 h-2.5 mr-0.5" /> : <TrendingDown className="w-2.5 h-2.5 mr-0.5" />}
            {bdiChange > 0 ? `+${bdiChange}%` : `${bdiChange}%`}
          </span>
        </div>

        {/* Weather Intelligence Badge */}
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${severityBadgeClass}`}>
          <CloudLightning className="w-3.5 h-3.5" />
          <span className="font-semibold text-[11px]">Weather Risk:</span>
          <span className="font-extrabold uppercase">{weatherSeverity}</span>
          {weatherAdj > 0 && (
            <span className="bg-amber-400/20 text-amber-300 text-[10px] px-1.5 py-0.2 rounded font-mono font-bold">
              +{weatherAdj}% Rate Adj
            </span>
          )}
        </div>

        {/* Active Alerts Count */}
        {weatherAlertsCount > 0 && (
          <span className="bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping" />
            {weatherAlertsCount} Active Warning{weatherAlertsCount > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Right: Manual Poll Action */}
      <button
        onClick={onRefresh}
        disabled={loading}
        className="flex items-center gap-1.5 px-2.5 py-1 bg-[#16305c] hover:bg-[#1f427d] text-slate-200 hover:text-white rounded-lg transition-all font-semibold text-[11px] disabled:opacity-50 border border-[#2b5394]"
        title="Trigger live scheduler refresh"
      >
        <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        <span>{loading ? 'Updating...' : 'Sync Now'}</span>
      </button>
    </div>
  );
}
