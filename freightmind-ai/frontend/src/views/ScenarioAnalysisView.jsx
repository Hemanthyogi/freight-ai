import React, { useState } from 'react';
import {
  GitCompare,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  TrendingUp,
  Shield,
  DollarSign,
  ArrowRight,
  Sliders,
  Sparkles
} from 'lucide-react';

export default function ScenarioAnalysisView({ dashboardData }) {
  const [rateShockPct, setRateShockPct] = useState(0);

  const baseScenarios = [
    {
      id: 'A',
      name: 'Scenario A: Spot Charter',
      badge: 'HIGH VOLATILITY',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-300',
      baseFreight: 10.40,
      baseCost: 2948750,
      riskLevel: 'MEDIUM - HIGH',
      volatilityExp: 'High - Fully exposed to day-to-day spot fixture spikes & bunker spikes',
      flexibility: 'Maximum - Single voyage commitment with no forward lock-in',
      tonnageSecurity: 'Low - Subject to prompt spot availability in loading window',
      pros: [
        'Zero forward volume or laycan lock-in',
        'Can pause shipments instantly if plant inventory swells',
      ],
      cons: [
        'Pays spot liquidity premium (~5-8%)',
        'Vulnerable to freight rate rallies and port congestion demurrage',
      ],
    },
    {
      id: 'B',
      name: 'Scenario B: AI Optimal (Multiple Voyage)',
      badge: 'AI OPTIMAL RECOMMENDATION',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      baseFreight: 9.60,
      baseCost: 2720750,
      riskLevel: 'LOW',
      volatilityExp: 'Low - Locks agreed index-linked collar across 3-month tranche',
      flexibility: 'Moderate - Agreed laycan schedule with ±5 days laycan spread',
      tonnageSecurity: 'High - Dedicated vessel or guaranteed performing tonnage',
      pros: [
        'Saves ~$228,000+ compared to unhedged spot charters',
        'Guaranteed vessel availability during peak procurement months',
        'Eliminates stockout risk for steel and power plants',
      ],
      cons: [
        'Requires committed cargo readiness and demurrage discipline',
      ],
    },
    {
      id: 'C',
      name: 'Scenario C: Delayed Charter (Postpone >3 Weeks)',
      badge: 'HIGH PROCUREMENT RISK',
      badgeColor: 'bg-red-100 text-red-800 border-red-300',
      baseFreight: 10.91,
      baseCost: 3146380,
      riskLevel: 'HIGH',
      volatilityExp: 'Very High - High probability of entering market during forward supply crunch',
      flexibility: 'Low - Constrained tonnage options near immediate laycan',
      tonnageSecurity: 'Very Low - Last-minute fixtures incur steep demurrage and hire premiums',
      pros: [
        'Short-term cash conservation in immediate 2-week window',
      ],
      cons: [
        'Highest expected total landed voyage expenditure',
        'Severe risk of factory shutdown due to raw material stockout',
      ],
    },
  ];

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Strategic Decision Support
              </span>
              <span className="text-xs text-slate-400">Target Cargo: 250,000 MT Iron Ore | Indonesia → Paradip</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <GitCompare className="w-6 h-6 text-blue-400" />
              Strategic Scenario & Risk Analysis
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Side-by-side trade-off evaluation comparing Spot Market Fixtures, AI-Optimized Multiple-Voyage Charter Contracts, and Postponed/Delayed Market Entry.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm p-3 rounded-xl border border-white/10">
            <div className="text-right">
              <p className="text-[10px] uppercase font-bold text-slate-400">Net Scenario B Savings</p>
              <p className="text-2xl font-black text-emerald-400">+$228k <span className="text-xs font-medium text-slate-300">vs Spot</span></p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-emerald-600/30 flex items-center justify-center text-emerald-300">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      {/* Market Volatility Stress-Test Slider */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-blue-600" />
          <div>
            <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">
              Market Rate Shock Sensitivity Simulator
            </h3>
            <p className="text-xs text-slate-500">
              Simulate market shocks (e.g. bunker price spikes or geopolitical chokepoint delays)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-slate-700">Market Rate Shock:</span>
          <div className="flex items-center gap-1.5">
            {[-10, 0, 10, 20].map((val) => (
              <button
                key={val}
                onClick={() => setRateShockPct(val)}
                className={`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${
                  rateShockPct === val
                    ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                    : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                {val > 0 ? `+${val}%` : `${val}%`}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 3 Expanded Scenario Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {baseScenarios.map((s) => {
          const isOptimal = s.id === 'B';
          const multiplier = 1 + rateShockPct / 100;
          const adjustedRate = s.id === 'B'
            ? s.baseFreight * (1 + (rateShockPct * 0.4) / 100) // Scenario B has hedging collar dampener
            : s.baseFreight * multiplier;
          const adjustedCost = s.id === 'B'
            ? s.baseCost * (1 + (rateShockPct * 0.4) / 100)
            : s.baseCost * multiplier;

          return (
            <div
              key={s.id}
              className={`bg-white rounded-2xl p-5 border flex flex-col justify-between transition-all ${
                isOptimal
                  ? 'border-emerald-300 shadow-lg shadow-emerald-600/10 ring-2 ring-emerald-300'
                  : 'border-slate-200 shadow-sm hover:border-slate-300'
              }`}
            >
              <div className="space-y-4">
                {/* Header */}
                <div className="border-b border-slate-100 pb-3">
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider border ${s.badgeColor}`}>
                      {s.badge}
                    </span>
                    <span className="text-xs font-bold text-slate-400">Risk: {s.riskLevel}</span>
                  </div>
                  <h3 className="text-base font-black text-slate-900">{s.name}</h3>
                </div>

                {/* Price & Cost Box */}
                <div className={`p-4 rounded-xl border ${isOptimal ? 'bg-emerald-50/60 border-emerald-200' : 'bg-slate-50 border-slate-100'}`}>
                  <div className="flex justify-between items-baseline mb-1">
                    <span className="text-xs text-slate-500">Unit Freight:</span>
                    <span className="text-xl font-black text-slate-900">${adjustedRate.toFixed(2)} <span className="text-xs font-normal">/ MT</span></span>
                  </div>
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-slate-500">Total Landed Cost:</span>
                    <span className="text-base font-black text-blue-600">${(adjustedCost / 1e6).toFixed(2)}M</span>
                  </div>
                </div>

                {/* Characteristics */}
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="font-bold text-slate-500 text-[10px] uppercase">Price Volatility Exposure</span>
                    <p className="text-slate-800">{s.volatilityExp}</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-500 text-[10px] uppercase">Operational Flexibility</span>
                    <p className="text-slate-800">{s.flexibility}</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-500 text-[10px] uppercase">Tonnage Security</span>
                    <p className="text-slate-800">{s.tonnageSecurity}</p>
                  </div>
                </div>

                {/* Pros & Cons */}
                <div className="space-y-2 pt-2 border-t border-slate-100 text-xs">
                  <div>
                    <p className="font-bold text-emerald-700 flex items-center gap-1 mb-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Advantages
                    </p>
                    <ul className="space-y-1 text-slate-600 pl-4 list-disc text-[11px]">
                      {s.pros.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="pt-1">
                    <p className="font-bold text-amber-700 flex items-center gap-1 mb-1">
                      <AlertTriangle className="w-3.5 h-3.5" /> Trade-offs
                    </p>
                    <ul className="space-y-1 text-slate-600 pl-4 list-disc text-[11px]">
                      {s.cons.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Card Footer Button */}
              <div className="pt-4 mt-4 border-t border-slate-100">
                <button
                  className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all shadow-sm ${
                    isOptimal
                      ? 'bg-emerald-600 hover:bg-emerald-700 text-white'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                  }`}
                >
                  {isOptimal ? 'Select Scenario B (Recommended)' : 'Evaluate Alternative Terms'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
