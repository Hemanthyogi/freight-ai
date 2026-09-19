import React from 'react';
import { HelpCircle, CheckCircle2, Ship } from 'lucide-react';

export default function WhyRecommendation({ reasons, quote }) {
  const defaultReasons = [
    'Favorable freight-rate forecast: AI predicts lower rates in the coming weeks.',
    'Vessel capacity matches cargo requirement: MV Ocean Crest (58,000 DWT) fits 250,000 MT across multiple voyages.',
    'Lower port congestion and voyage risk: East Coast ports are operating efficiently with manageable weather risk.',
  ];

  const list = reasons && reasons.length > 0 ? reasons : defaultReasons;

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <HelpCircle className="w-5 h-5 text-blue-600" />
        <h2 className="text-xs font-black uppercase tracking-wider text-slate-800">
          WHY THIS RECOMMENDATION?
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-center">
        {/* Bullets List (2 cols) */}
        <div className="md:col-span-2 space-y-2">
          {list.map((reason, idx) => (
            <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 leading-relaxed">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>{reason}</span>
            </div>
          ))}
        </div>

        {/* Motivational Right Quote Tile (1 col) */}
        <div className="p-3.5 rounded-xl bg-gradient-to-br from-indigo-900 to-blue-950 text-white flex flex-col justify-between h-full shadow-sm relative overflow-hidden">
          <div className="relative z-10 flex items-center gap-2 text-indigo-300 mb-1">
            <Ship className="w-4 h-4" />
            <span className="text-[10px] font-bold uppercase tracking-wider">MARITIME VISION</span>
          </div>
          <p className="relative z-10 text-[11px] font-semibold italic text-blue-100 leading-snug">
            "{quote || 'Optimized chartering today for a more resilient and cost-efficient tomorrow.'}"
          </p>
          <Ship className="w-16 h-16 text-white/5 absolute -right-2 -bottom-2 pointer-events-none" />
        </div>
      </div>
    </div>
  );
}
