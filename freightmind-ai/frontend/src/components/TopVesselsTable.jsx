import React from 'react';
import { Ship, ExternalLink } from 'lucide-react';

export default function TopVesselsTable({ vessels, onSelectVessel }) {
  const defaultList = [
    {
      vessel_id: 'V0006',
      vessel_name: 'MV Ocean Crest',
      dwt_mt: 58000,
      eta: '18 Sep',
      match_score: 94,
      freight_rate_usd_mt: 31.9,
      risk_level: 'LOW',
    },
    {
      vessel_id: 'V0007',
      vessel_name: 'MV Eastern Star',
      dwt_mt: 62000,
      eta: '21 Sep',
      match_score: 89,
      freight_rate_usd_mt: 32.4,
      risk_level: 'LOW',
    },
    {
      vessel_id: 'V0008',
      vessel_name: 'MV Pacific Trader',
      dwt_mt: 55000,
      eta: '25 Sep',
      match_score: 83,
      freight_rate_usd_mt: 33.1,
      risk_level: 'MED',
    },
  ];

  const list = vessels && vessels.length > 0 ? vessels : defaultList;

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
      {/* Table Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Ship className="w-5 h-5 text-blue-600" />
          <h2 className="text-xs font-black uppercase tracking-wider text-slate-800">
            TOP VESSEL MATCHES
          </h2>
        </div>
        <button className="text-[11px] font-bold text-blue-600 hover:text-blue-800 flex items-center gap-1">
          <span>View All</span>
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-[10px] uppercase font-bold text-slate-400">
              <th className="pb-2">VESSEL</th>
              <th className="pb-2">DWT</th>
              <th className="pb-2">ETA</th>
              <th className="pb-2 text-center">MATCH SCORE</th>
              <th className="pb-2">FREIGHT</th>
              <th className="pb-2">RISK</th>
              <th className="pb-2 text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium">
            {list.map((v, idx) => {
              const isFirst = idx === 0;
              const isHighMatch = v.match_score >= 85;
              return (
                <tr key={v.vessel_id || idx} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-slate-600 shrink-0">
                        <Ship className="w-3.5 h-3.5" />
                      </div>
                      <span className="font-bold text-slate-900">{v.vessel_name}</span>
                    </div>
                  </td>
                  <td className="py-2.5 text-slate-600">{Math.round(v.dwt_mt / 1000)}K</td>
                  <td className="py-2.5 text-slate-600">{v.eta}</td>
                  <td className="py-2.5 text-center">
                    <span
                      className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-[11px] font-black ${
                        isHighMatch
                          ? 'bg-emerald-50 text-emerald-700 border-2 border-emerald-500'
                          : 'bg-amber-50 text-amber-700 border-2 border-amber-500'
                      }`}
                    >
                      {v.match_score}%
                    </span>
                  </td>
                  <td className="py-2.5 font-bold text-slate-900">
                    ${v.freight_rate_usd_mt} / MT
                  </td>
                  <td className="py-2.5">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        v.risk_level === 'LOW'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {v.risk_level}
                    </span>
                  </td>
                  <td className="py-2.5 text-right">
                    {isFirst ? (
                      <button
                        onClick={() => onSelectVessel && onSelectVessel(v)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-[11px] font-bold transition-all shadow-sm"
                      >
                        SELECT
                      </button>
                    ) : (
                      <button
                        onClick={() => onSelectVessel && onSelectVessel(v)}
                        className="px-3 py-1 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-md text-[11px] font-bold transition-all"
                      >
                        VIEW
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
