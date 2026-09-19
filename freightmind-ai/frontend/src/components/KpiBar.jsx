import React from 'react';
import {
  TrendingDown,
  CalendarCheck,
  Ship,
  CircleDollarSign,
  ShieldCheck,
  CheckCircle2,
  Anchor
} from 'lucide-react';

export default function KpiBar({ kpis }) {
  const data = kpis || {
    forecast_freight_rate: '$32.8 / MT',
    rate_change_expected: '6.4% expected',
    rate_change_pct: -6.4,
    chartering_window: '18 - 24 SEP',
    chartering_window_status: 'Favorable',
    vessel_availability_label: '12 Suitable',
    high_match_count: 3,
    expected_total_cost: '$2.84M',
    cost_status: 'Optimized',
    risk_level: 'LOW - MEDIUM',
    risk_score: 28,
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
      {/* 1. Forecast Freight Rate */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-sm flex items-start justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            FORECAST FREIGHT RATE
          </span>
          <div className="text-xl font-black text-slate-900 mt-1">
            {data.forecast_freight_rate}
          </div>
          <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-600 mt-1">
            <TrendingDown className="w-3.5 h-3.5" />
            <span>{data.rate_change_expected || '6.4% expected'}</span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
          <TrendingDown className="w-5 h-5" />
        </div>
      </div>

      {/* 2. Chartering Window */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-sm flex items-start justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            CHARTERING WINDOW
          </span>
          <div className="text-xl font-black text-slate-900 mt-1">
            {data.chartering_window}
          </div>
          <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-600 mt-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{data.chartering_window_status}</span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
          <CalendarCheck className="w-5 h-5" />
        </div>
      </div>

      {/* 3. Vessel Availability */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-sm flex items-start justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            VESSEL AVAILABILITY
          </span>
          <div className="text-xl font-black text-slate-900 mt-1">
            {data.vessel_availability_label}
          </div>
          <div className="flex items-center gap-1 text-[11px] font-bold text-slate-600 mt-1">
            <Ship className="w-3.5 h-3.5 text-blue-600" />
            <span>{data.high_match_count} High Match</span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center shrink-0">
          <Ship className="w-5 h-5" />
        </div>
      </div>

      {/* 4. Expected Total Cost */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-sm flex items-start justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            EXPECTED TOTAL COST
          </span>
          <div className="text-xl font-black text-slate-900 mt-1">
            {data.expected_total_cost}
          </div>
          <div className="flex items-center gap-1 text-[11px] font-bold text-emerald-600 mt-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{data.cost_status}</span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
          <CircleDollarSign className="w-5 h-5" />
        </div>
      </div>

      {/* 5. Risk Level */}
      <div className="bg-white rounded-xl p-3.5 border border-slate-200 shadow-sm flex items-start justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            RISK LEVEL
          </span>
          <div className="text-xl font-black text-slate-900 mt-1">
            {data.risk_level}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-600 mt-1">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>Score: {data.risk_score}/100</span>
          </div>
        </div>
        <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
          <ShieldCheck className="w-5 h-5" />
        </div>
      </div>

      {/* 6. Promotional Graphic Tile */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-950 rounded-xl p-3 text-white flex flex-col justify-between shadow-sm relative overflow-hidden">
        <div className="relative z-10">
          <span className="text-[9px] font-bold uppercase tracking-widest text-blue-300">
            MARITIME EXCELLENCE
          </span>
          <p className="text-xs font-black leading-tight mt-1 text-white">
            Efficient Logistics for a Stronger Nation
          </p>
        </div>
        <div className="relative z-10 flex items-center gap-1 text-[10px] font-semibold text-blue-200">
          <Anchor className="w-3 h-3 text-blue-400" />
          <span>Sagarmala Aligned</span>
        </div>
        <Ship className="w-16 h-16 text-white/5 absolute -right-2 -bottom-2 pointer-events-none" />
      </div>
    </div>
  );
}
