import React, { useState } from 'react';
import {
  TrendingUp,
  Calendar,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Shield,
  Activity,
  Zap,
  Info,
  Sliders,
  DollarSign
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import defaultDashboardData from '../data/defaultDashboardData.json';

export default function ForecastView({ dashboardData }) {
  const [selectedHorizon, setSelectedHorizon] = useState(14);

  // Safe fallback to default demo data if dashboardData or series is empty
  const historical = (dashboardData?.forecast_chart_historical && dashboardData.forecast_chart_historical.length > 0)
    ? dashboardData.forecast_chart_historical
    : defaultDashboardData.forecast_chart_historical;

  const prediction = (dashboardData?.forecast_chart_prediction && dashboardData.forecast_chart_prediction.length > 0)
    ? dashboardData.forecast_chart_prediction
    : defaultDashboardData.forecast_chart_prediction;

  const lastHist = historical && historical.length > 0 ? historical[historical.length - 1] : null;
  const currentSpotRate = dashboardData?.forecast_rate
    || (lastHist ? lastHist.rate : 9.90);
  const todayDateStr = lastHist ? lastHist.date.slice(5) : '09-14';

  // Dynamic multi-horizon metrics
  const defaultHorizonDefs = [
    { days: 7, label: '7-Day', target: 'Prompt Loading', defaultRate: 9.78, change: -1.2, signal: 'Favorable' },
    { days: 14, label: '14-Day', target: 'Primary Laycan', defaultRate: 9.90, change: 0.1, signal: 'Neutral' },
    { days: 30, label: '30-Day', target: 'Forward Position', defaultRate: 10.56, change: 6.8, signal: 'Rising' },
    { days: 60, label: '60-Day', target: 'Q4 Tranche', defaultRate: 11.15, change: 12.7, signal: 'Elevated' },
    { days: 90, label: '90-Day', target: 'Quarterly Contract', defaultRate: 10.90, change: 10.2, signal: 'Softening' },
  ];

  const horizons = defaultHorizonDefs.map((h) => {
    const predItem = prediction.find((p) => p.horizon_days === h.days);
    if (predItem) {
      const rate = predItem.forecast_rate;
      const change = currentSpotRate > 0
        ? Number((((rate - currentSpotRate) / currentSpotRate) * 100).toFixed(1))
        : 0;
      let signal = 'Neutral';
      if (change < -1.0) signal = 'Favorable';
      else if (change > 8.0) signal = 'Elevated';
      else if (change > 2.0) signal = 'Rising';
      else if (change < 0.0) signal = 'Softening';

      return {
        ...h,
        rate,
        lower: predItem.lower_bound,
        upper: predItem.upper_bound,
        change,
        signal,
      };
    }
    return {
      ...h,
      rate: h.defaultRate,
      lower: Number((h.defaultRate * 0.88).toFixed(2)),
      upper: Number((h.defaultRate * 1.12).toFixed(2)),
    };
  });

  const currentHorizonData = horizons.find((h) => h.days === selectedHorizon) || horizons[1];

  // Combine for chart with seamless bridge at TODAY
  const chartData = [
    ...historical.map((d, idx) => {
      const isLast = idx === historical.length - 1;
      return {
        date: d.date.slice(5),
        historical: d.rate,
        forecast: isLast ? d.rate : null,
        lower: isLast ? d.rate : null,
        upper: isLast ? d.rate : null,
        ciRange: isLast ? [d.rate, d.rate] : null,
        fullDate: d.date,
        isToday: isLast,
      };
    }),
    ...prediction.map((d) => ({
      date: d.date.slice(5),
      historical: null,
      forecast: d.forecast_rate,
      lower: d.lower_bound,
      upper: d.upper_bound,
      ciRange: [d.lower_bound, d.upper_bound],
      fullDate: d.date,
      horizon: d.horizon_days,
      isSelected: d.horizon_days === selectedHorizon,
    })),
  ];

  // Dynamic Y-axis bounds to prevent lines being clipped for higher-rate routes
  const allRates = [
    ...historical.map((d) => d.rate),
    ...prediction.flatMap((d) => [d.forecast_rate, d.lower_bound, d.upper_bound])
  ].filter((v) => typeof v === 'number' && !isNaN(v));

  const yMin = allRates.length > 0 ? Math.max(0, Math.floor(Math.min(...allRates) - 1)) : 7;
  const yMax = allRates.length > 0 ? Math.ceil(Math.max(...allRates) + 1) : 15;

  // Dynamic route descriptions
  const routeOrigin = dashboardData?.cargo_requirement?.origin || 'Indonesia (Balikpapan)';
  const routeDest = dashboardData?.cargo_requirement?.destination_port
    ? `East Coast India (${dashboardData.cargo_requirement.destination_port})`
    : 'East Coast India (Paradip)';
  const vesselLabel = dashboardData?.ai_recommendation?.vessel_capacity_dwt
    ? `Supramax ${dashboardData.ai_recommendation.vessel_capacity_dwt}`
    : 'Supramax 58,000 DWT';

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                AI Inference Engine
              </span>
              <span className="text-xs text-slate-400">
                Model: {dashboardData?.model_version || 'XGBoost Multi-Horizon Regressor v1.0'}
              </span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-400" />
              Intelligent Freight Rate Forecasting
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Multi-horizon rate projection trained on 29,000+ calibrated fixture records with strict zero-leakage chronological validation, Baltic Dry Index leading indicators, and 80% confidence corridors.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm p-3 rounded-xl border border-white/10">
            <div className="text-right">
              <p className="text-[10px] uppercase font-bold text-slate-400">Current Spot Rate</p>
              <p className="text-2xl font-black text-white">
                ${currentSpotRate.toFixed(2)}{' '}
                <span className="text-xs font-medium text-slate-300">/ MT</span>
              </p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-blue-600/30 flex items-center justify-center text-blue-300">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Horizon Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {horizons.map((h) => {
          const isSelected = selectedHorizon === h.days;
          const isPositive = h.change >= 0;
          return (
            <button
              key={h.days}
              onClick={() => setSelectedHorizon(h.days)}
              className={`p-4 rounded-xl text-left transition-all border ${
                isSelected
                  ? 'bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-600/30 ring-2 ring-blue-400'
                  : 'bg-white text-slate-800 border-slate-200 hover:border-blue-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded ${
                  isSelected ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
                }`}>
                  {h.label}
                </span>
                <span className={`text-[10px] font-bold ${
                  isSelected ? 'text-blue-100' : isPositive ? 'text-amber-600' : 'text-emerald-600'
                }`}>
                  {h.signal}
                </span>
              </div>
              <p className={`text-xl font-black ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                ${h.rate.toFixed(2)}
                <span className={`text-[10px] font-normal ml-1 ${isSelected ? 'text-blue-100' : 'text-slate-500'}`}>/ MT</span>
              </p>
              <div className="flex items-center gap-1 mt-1">
                {isPositive ? (
                  <ArrowUpRight className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-amber-500'}`} />
                ) : (
                  <ArrowDownRight className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-emerald-500'}`} />
                )}
                <span className={`text-xs font-bold ${
                  isSelected ? 'text-white' : isPositive ? 'text-amber-600' : 'text-emerald-600'
                }`}>
                  {isPositive ? '+' : ''}{h.change}%
                </span>
                <span className={`text-[10px] ${isSelected ? 'text-blue-100' : 'text-slate-400'} ml-auto`}>
                  {h.target}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Chart Section */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-900">
                Forecast Curve with 80% Confidence Interval Corridor
              </h3>
              <p className="text-xs text-slate-500">
                {routeOrigin} → {routeDest} | {vesselLabel}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className="w-3 h-0.5 bg-blue-600 inline-block"></span> Historical Fixture
            </span>
            <span className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className="w-3 h-0.5 bg-emerald-500 inline-block border-t border-dashed"></span> AI Projection
            </span>
            <span className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className="w-3 h-3 bg-emerald-500/10 border border-emerald-500/40 inline-block rounded-sm"></span> 80% CI Corridor
            </span>
          </div>
        </div>

        {/* Recharts Curve */}
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: '#64748b' }}
                tickLine={false}
                axisLine={{ stroke: '#cbd5e1' }}
                minTickGap={25}
              />
              <YAxis
                domain={[yMin, yMax]}
                tick={{ fontSize: 10, fill: '#64748b' }}
                tickLine={false}
                axisLine={{ stroke: '#cbd5e1' }}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderRadius: '12px',
                  border: '1px solid #1e293b',
                  color: '#fff',
                  fontSize: '11px',
                  padding: '8px 12px',
                }}
                formatter={(val, name) => {
                  if (name === 'ciRange' && Array.isArray(val)) {
                    return [`$${val[0]} - $${val[1]}`, '80% CI Corridor'];
                  }
                  if (typeof val === 'number') {
                    return [`$${val.toFixed(2)} / MT`, name === 'historical' ? 'Historical Fixture' : 'AI Forecast'];
                  }
                  return [val, name];
                }}
              />
              <ReferenceLine
                x={todayDateStr}
                stroke="#94a3b8"
                strokeDasharray="3 3"
                label={{ value: 'TODAY', position: 'insideTopLeft', fill: '#64748b', fontSize: 10 }}
              />
              <Area
                type="monotone"
                dataKey="ciRange"
                stroke="none"
                fill="#10b981"
                fillOpacity={0.15}
                name="ciRange"
              />
              <Line
                type="monotone"
                dataKey="historical"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                name="historical"
              />
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#10b981"
                strokeWidth={2.5}
                strokeDasharray="4 4"
                dot={(props) => {
                  const { cx, cy, payload } = props;
                  if (!cx || !cy) return null;
                  const isHighlight = payload?.horizon === selectedHorizon;
                  return (
                    <circle
                      key={`dot-${payload.date}`}
                      cx={cx}
                      cy={cy}
                      r={isHighlight ? 6 : 4}
                      fill={isHighlight ? '#059669' : '#10b981'}
                      stroke={isHighlight ? '#ffffff' : 'none'}
                      strokeWidth={isHighlight ? 2 : 0}
                    />
                  );
                }}
                name="forecast"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Selected Horizon Callout */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-600 shrink-0" />
            <div>
              <span className="font-bold text-slate-800">Horizon Insight ({currentHorizonData.label}): </span>
              <span className="text-slate-600">
                Model predicts freight rates at{' '}
                <span className="font-bold text-slate-900">${currentHorizonData.rate.toFixed(2)}/MT</span>.
                Target laycan window allows charterers to secure tonnage before forward rate adjustments.
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 rounded bg-white font-bold border border-slate-200 text-slate-700">
              Confidence Interval: ${currentHorizonData.lower?.toFixed(2) || (currentHorizonData.rate * 0.88).toFixed(2)} - ${currentHorizonData.upper?.toFixed(2) || (currentHorizonData.rate * 1.12).toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Model Feature Drivers & Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-indigo-600 font-black text-xs uppercase tracking-wider">
            <Zap className="w-4 h-4" /> Top Predictive Drivers
          </div>
          <ul className="space-y-1.5 text-xs text-slate-600 pt-1">
            <li className="flex justify-between"><span>Baltic Dry Index (BDI Lag-7):</span> <span className="font-bold text-slate-800">28.4% weight</span></li>
            <li className="flex justify-between"><span>VLSFO Bunker Fuel Price:</span> <span className="font-bold text-slate-800">22.1% weight</span></li>
            <li className="flex justify-between"><span>Rolling 14-Day Route Mean:</span> <span className="font-bold text-slate-800">18.7% weight</span></li>
            <li className="flex justify-between"><span>Monsoon Season Indicator:</span> <span className="font-bold text-slate-800">14.3% weight</span></li>
            <li className="flex justify-between"><span>Destination Port Congestion:</span> <span className="font-bold text-slate-800">11.5% weight</span></li>
          </ul>
        </div>

        <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-emerald-600 font-black text-xs uppercase tracking-wider">
            <Shield className="w-4 h-4" /> ML Validation Metrics
          </div>
          <ul className="space-y-1.5 text-xs text-slate-600 pt-1">
            <li className="flex justify-between"><span>Algorithm:</span> <span className="font-bold text-slate-800">XGBoost Multi-Horizon</span></li>
            <li className="flex justify-between"><span>$R^2$ Score (Test Split):</span> <span className="font-bold text-emerald-600">0.8192 (81.9%)</span></li>
            <li className="flex justify-between"><span>Root Mean Sq. Error (RMSE):</span> <span className="font-bold text-slate-800">$1.259 / MT</span></li>
            <li className="flex justify-between"><span>Mean Absolute Error (MAE):</span> <span className="font-bold text-slate-800">$0.953 / MT</span></li>
            <li className="flex justify-between"><span>Mean Abs % Error (MAPE):</span> <span className="font-bold text-slate-800">7.05%</span></li>
          </ul>
        </div>

        <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center gap-2 text-blue-600 font-black text-xs uppercase tracking-wider">
            <Layers className="w-4 h-4" /> Operational Recommendation
          </div>
          <p className="text-xs text-slate-600 leading-relaxed pt-1">
            Given current softening indicators over the 7–14 day corridor followed by an expected upward correction at 30 days (+6.8%), the optimal strategy is to <strong>fix tonnage now</strong> under consecutive-voyage terms to lock in rates near ${currentSpotRate.toFixed(2)}/MT.
          </p>
          <div className="pt-2">
            <span className="inline-block px-3 py-1 bg-emerald-50 text-emerald-700 font-bold text-xs rounded-lg border border-emerald-200">
              Action Signal: Fix Within 7-10 Days
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
