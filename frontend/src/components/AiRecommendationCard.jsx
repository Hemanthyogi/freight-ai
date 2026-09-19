import React from 'react';
import {
  Target,
  Ship,
  ArrowRight,
  Compass,
  Calendar,
  DollarSign,
  Calculator,
  ShieldAlert
} from 'lucide-react';

export default function AiRecommendationCard({ recommendation, onPlanClick }) {
  const rec = recommendation || {
    action: 'CHARTER',
    vessel_name: 'MV Ocean Crest',
    vessel_capacity_dwt: '58,000 DWT',
    route_display: 'Indonesia -> East Coast India',
    chartering_window: '18 - 24 SEP',
    expected_freight_usd_mt: 31.9,
    expected_total_cost_formatted: '$2.84M',
    risk_score: 28,
    risk_level_label: 'LOW - MEDIUM',
  };

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <Target className="w-5 h-5 text-indigo-600" />
        <h2 className="text-xs font-black uppercase tracking-wider text-slate-800">
          AI CHARTERING RECOMMENDATION
        </h2>
      </div>

      {/* Recommended Action Badge */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3 flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-600 text-white flex items-center justify-center shadow-md shadow-emerald-600/20">
            <Ship className="w-6 h-6" />
          </div>
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-800">
              RECOMMENDED ACTION
            </div>
            <div className="text-lg font-black text-emerald-700 tracking-wide">
              {rec.action || 'CHARTER'}
            </div>
          </div>
        </div>
      </div>

      {/* Details Grid */}
      <div className="space-y-2.5 text-xs">
        {/* Vessel & Capacity */}
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
          <div className="flex items-center gap-2 text-slate-700">
            <Ship className="w-4 h-4 text-blue-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">VESSEL</div>
              <div className="font-bold text-slate-900">{rec.vessel_name}</div>
            </div>
          </div>
          <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
          <div className="text-right">
            <div className="text-[9px] font-bold uppercase text-slate-400">CAPACITY</div>
            <div className="font-bold text-slate-900">{rec.vessel_capacity_dwt}</div>
          </div>
        </div>

        {/* Route */}
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-indigo-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">ROUTE</div>
              <div className="font-bold text-slate-900">{rec.route_display}</div>
            </div>
          </div>
        </div>

        {/* Window & Expected Freight */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-emerald-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">CHARTERING WINDOW</div>
              <div className="font-bold text-slate-900">{rec.chartering_window}</div>
            </div>
          </div>
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-emerald-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">EXPECTED FREIGHT</div>
              <div className="font-bold text-slate-900">${rec.expected_freight_usd_mt} / MT</div>
            </div>
          </div>
        </div>

        {/* Expected Total Cost & Risk Score */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-blue-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">EXPECTED TOTAL COST</div>
              <div className="font-bold text-slate-900">{rec.expected_total_cost_formatted}</div>
            </div>
          </div>
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">RISK SCORE</div>
              <div className="font-bold text-slate-900">{rec.risk_score} / 100</div>
            </div>
          </div>
        </div>
      </div>

      {/* Button */}
      <button
        onClick={onPlanClick}
        className="w-full mt-3 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-md shadow-indigo-600/30"
      >
        <span>VIEW OPTIMAL PLAN</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
