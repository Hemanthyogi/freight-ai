import React, { useState } from 'react';
import {
  FileText,
  Download,
  BarChart3,
  TrendingUp,
  Shield,
  Layers,
  CheckCircle2,
  ExternalLink,
  Maximize2,
  X,
  FileSpreadsheet,
  Award
} from 'lucide-react';

export default function ReportsView({ dashboardData }) {
  const [activeFigure, setActiveFigure] = useState(null);

  const figures = [
    {
      id: '01',
      title: '01. Freight Trends by Route (2020-2026)',
      src: '/figures/01_freight_trends_by_route.png',
      desc: 'Historical daily freight rate series across Australia, Indonesia, and South Africa corridors showing post-COVID normalization and route spreads.',
    },
    {
      id: '02',
      title: '02. Vessel Class Rate Comparison & Economies of Scale',
      src: '/figures/02_vessel_class_rate_comparison.png',
      desc: 'Unit rate comparison ($/MT) showing clear economies of scale: Capesize ($11.21/MT) vs Panamax ($13.56/MT) vs Supramax ($15.86/MT).',
    },
    {
      id: '03',
      title: '03. Seasonal Patterns & Indian Monsoon Discount',
      src: '/figures/03_seasonal_and_monthly_patterns.png',
      desc: 'Seasonal rate contraction during June-September Indian monsoon (-7.74% discount) due to sea-state and regional port loading operations.',
    },
    {
      id: '04',
      title: '04. Macro Correlation Matrix (BDI, Bunker, Commodities)',
      src: '/figures/04_macro_correlation_heatmap.png',
      desc: 'Cross-feature correlation matrix confirming Baltic Dry Index (+0.482) and VLSFO bunker fuel as strong leading predictors of freight fixtures.',
    },
    {
      id: '05',
      title: '05. East Coast India Port Congestion & Waiting Analysis',
      src: '/figures/05_port_congestion_and_waiting.png',
      desc: 'Port waiting time distributions: Haldia (78.1h avg wait) vs Paradip (40.4h) vs Gopalpur (15.6h) across 17,000+ vessel calls.',
    },
    {
      id: '06',
      title: '06. Multi-Horizon Forecast vs Actual Out-of-Sample Test',
      src: '/figures/06_forecast_vs_actual.png',
      desc: 'Model performance on 4,356 test rows showing tight tracking of turning points and calibrated 80% prediction interval coverage.',
    },
  ];

  const models = [
    { name: 'XGBoost Regressor (Selected)', mae: 0.953, rmse: 1.259, mape: '7.05%', r2: 0.8192, time: '16.4s', selected: true },
    { name: 'Naive Persistence (Baseline)', mae: 0.949, rmse: 1.277, mape: '6.95%', r2: 0.8142, time: '0.00s', selected: false },
    { name: 'LightGBM Regressor', mae: 0.967, rmse: 1.281, mape: '7.15%', r2: 0.8127, time: '2.8s', selected: false },
    { name: 'Moving Average (7-Day)', mae: 0.999, rmse: 1.323, mape: '7.34%', r2: 0.8004, time: '0.00s', selected: false },
    { name: 'Random Forest Regressor', mae: 1.006, rmse: 1.321, mape: '7.44%', r2: 0.8010, time: '14.1s', selected: false },
    { name: 'Moving Average (14-Day)', mae: 1.039, rmse: 1.360, mape: '7.66%', r2: 0.7890, time: '0.00s', selected: false },
  ];

  const handleExportJson = () => {
    const jsonStr = JSON.stringify(dashboardData || {}, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'freightmind_voyage_analysis_report.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Documentation & Verification Hub
              </span>
              <span className="text-xs text-slate-400">Smart India Hackathon 2026 | PS 26006</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <FileText className="w-6 h-6 text-blue-400" />
              Empirical Reports & ML Benchmarks
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Complete analytical reports, publication figures, exploratory data analysis findings, and machine learning model validation tables.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportJson}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-md"
            >
              <Download className="w-4 h-4" />
              Export Analysis JSON
            </button>
          </div>
        </div>
      </div>

      {/* Model Benchmark Table */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-600" />
            <h3 className="text-sm font-black text-slate-900">
              Model Performance Benchmark Table (14-Day Forecast Horizon, Test Partition)
            </h3>
          </div>
          <span className="text-[11px] font-bold text-slate-500">Chronological Split: 4,356 Test Observations</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] font-black tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Model Architecture</th>
                <th className="py-2.5 px-3">MAE ($/MT)</th>
                <th className="py-2.5 px-3">RMSE ($/MT)</th>
                <th className="py-2.5 px-3">MAPE (%)</th>
                <th className="py-2.5 px-3">R² Score</th>
                <th className="py-2.5 px-3">Training Time</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {models.map((m) => (
                <tr key={m.name} className={m.selected ? 'bg-emerald-50/60 font-semibold' : 'hover:bg-slate-50'}>
                  <td className="py-2.5 px-3 text-slate-900 flex items-center gap-2">
                    {m.selected && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                    <span>{m.name}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-700">${m.mae.toFixed(3)}</td>
                  <td className="py-2.5 px-3 text-slate-700">${m.rmse.toFixed(3)}</td>
                  <td className="py-2.5 px-3 text-slate-700">{m.mape}</td>
                  <td className={`py-2.5 px-3 font-bold ${m.selected ? 'text-emerald-700' : 'text-slate-700'}`}>
                    {(m.r2 * 100).toFixed(2)}% ({m.r2})
                  </td>
                  <td className="py-2.5 px-3 text-slate-500">{m.time}</td>
                  <td className="py-2.5 px-3">
                    {m.selected ? (
                      <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-emerald-100 text-emerald-800">
                        Production
                      </span>
                    ) : (
                      <span className="text-slate-400 text-[10px]">Benchmark</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Publication Figures Gallery */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-blue-600" />
          <h3 className="text-sm font-black text-slate-900 uppercase tracking-wider">
            Publication Figures & Analytical Charts (Click to Enlarge)
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {figures.map((fig) => (
            <div
              key={fig.id}
              onClick={() => setActiveFigure(fig)}
              className="group bg-white rounded-2xl p-4 border border-slate-200 shadow-sm hover:border-blue-300 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
            >
              <div>
                <div className="relative rounded-xl overflow-hidden bg-slate-100 border border-slate-100 mb-3 aspect-[16/10] flex items-center justify-center">
                  <img
                    src={fig.src}
                    alt={fig.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                  <div className="absolute inset-0 bg-slate-900/0 group-hover:bg-slate-900/20 transition-all flex items-center justify-center">
                    <Maximize2 className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-md" />
                  </div>
                </div>
                <h4 className="text-xs font-black text-slate-900 line-clamp-1 mb-1">{fig.title}</h4>
                <p className="text-[11px] text-slate-500 line-clamp-2">{fig.desc}</p>
              </div>

              <div className="pt-2 mt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-blue-600 font-bold">
                <span>View Full Resolution</span>
                <ExternalLink className="w-3 h-3" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Enlarged Figure Modal */}
      {activeFigure && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-black text-slate-900 text-base">{activeFigure.title}</h3>
                <p className="text-xs text-slate-500">{activeFigure.desc}</p>
              </div>
              <button
                onClick={() => setActiveFigure(null)}
                className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="rounded-xl overflow-hidden bg-slate-50 border border-slate-100 p-2 flex items-center justify-center max-h-[68vh]">
              <img
                src={activeFigure.src}
                alt={activeFigure.title}
                className="max-h-[64vh] w-auto object-contain rounded-lg"
              />
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-100">
              <button
                onClick={() => setActiveFigure(null)}
                className="px-5 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
              >
                Close Viewer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
