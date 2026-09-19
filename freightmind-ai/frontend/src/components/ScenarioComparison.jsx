import React from 'react';
import { GitCompare, CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-react';

export default function ScenarioComparison({ scenarios }) {
  const defaultScenarios = [
    {
      scenario_id: 'Scenario A',
      name: 'Spot Charter',
      badge: '',
      expected_cost_usd: 3120000,
      risk_level: 'Medium',
    },
    {
      scenario_id: 'Scenario B',
      name: 'Recommended',
      badge: 'AI OPTIMAL',
      expected_cost_usd: 2840000,
      risk_level: 'Low',
    },
    {
      scenario_id: 'Scenario C',
      name: 'Delayed Charter',
      badge: '',
      expected_cost_usd: 3260000,
      risk_level: 'High',
    },
  ];

  const list = scenarios && scenarios.length > 0 ? scenarios : defaultScenarios;

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <GitCompare className="w-5 h-5 text-blue-600" />
        <h2 className="text-xs font-black uppercase tracking-wider text-slate-800">
          SCENARIO COMPARISON
        </h2>
      </div>

      {/* 3 Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {list.map((s, idx) => {
          const isOptimal = s.badge === 'AI OPTIMAL' || s.name === 'Recommended';
          return (
            <div
              key={s.scenario_id || idx}
              className={`p-3 rounded-xl border relative transition-all ${
                isOptimal
                  ? 'bg-emerald-50/50 border-emerald-400 shadow-md shadow-emerald-500/10'
                  : 'bg-slate-50 border-slate-200'
              }`}
            >
              {/* Badge */}
              {isOptimal && (
                <div className="absolute -top-2.5 right-3 bg-emerald-600 text-white text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full shadow-sm">
                  AI OPTIMAL
                </div>
              )}

              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                {s.scenario_id}
              </div>
              <div className="text-xs font-black text-slate-900 mt-0.5 mb-2">
                {s.name}
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-[11px]">Expected Cost:</span>
                  <span className="font-extrabold text-slate-900">
                    ${(s.expected_cost_usd / 1e6).toFixed(2)}M
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-slate-600">Risk:</span>
                  <div className="flex items-center gap-1">
                    {s.risk_level === 'Low' && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3" />
                        Low
                      </span>
                    )}
                    {s.risk_level === 'Medium' && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="w-3 h-3" />
                        Medium
                      </span>
                    )}
                    {s.risk_level === 'High' && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded-full">
                        <AlertCircle className="w-3 h-3" />
                        High
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
