import React, { useState } from 'react';
import {
  Compass,
  Zap,
  Fuel,
  Gauge,
  Clock,
  DollarSign,
  Leaf,
  Shield,
  MapPin,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function OptimizationView({ dashboardData }) {
  const [speedKnots, setSpeedKnots] = useState(13.5);
  const [bunkerPrice, setBunkerPrice] = useState(580); // $/MT VLSFO

  const distanceNm = 2450;
  const portDays = 3.0; // Loading + discharge
  const charterRatePerDay = 16500; // $/day hire for Supramax

  // Transit days = distance / (speed * 24)
  const transitDays = distanceNm / (speedKnots * 24);
  const totalDays = transitDays + portDays;

  // Bunker burn cubic law: burn_mt_day = base * (speed / 14)^3
  const dailyBurnMt = 24.5 * Math.pow(speedKnots / 14.0, 3);
  const totalBunkerBurnMt = dailyBurnMt * transitDays + 3.0 * portDays; // 3mt/day in port
  const totalBunkerCost = totalBunkerBurnMt * bunkerPrice;
  const charterHireCost = totalDays * charterRatePerDay;
  const portDues = 35000;
  const totalVoyageCost = totalBunkerCost + charterHireCost + portDues;

  const co2EmissionsMt = totalBunkerBurnMt * 3.114; // IMO carbon factor

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Operational Optimization Engine
              </span>
              <span className="text-xs text-slate-400">Route: Indonesia (Balikpapan) → East Coast India (Paradip) | 2,450 NM</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <Compass className="w-6 h-6 text-blue-400" />
              Voyage Speed, Bunker & Cost Optimization
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Balances charter hire time vs. cubic bunker fuel curves to pinpoint the exact profit-maximizing sailing speed (Eco vs Design Speed) while cutting voyage carbon footprint.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm p-3 rounded-xl border border-white/10">
            <div className="text-right">
              <p className="text-[10px] uppercase font-bold text-slate-400">Optimized Voyage Cost</p>
              <p className="text-2xl font-black text-white">${(totalVoyageCost / 1000).toFixed(0)}k</p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-blue-600/30 flex items-center justify-center text-blue-300">
              <Zap className="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      {/* Speed & Bunker Trade-off Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-1 bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Gauge className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-black text-slate-900">Vessel Operating Parameters</h3>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Sailing Speed: {speedKnots} Knots
              </label>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                {speedKnots <= 12.5 ? 'Slow Steaming' : speedKnots <= 13.8 ? 'Eco Speed (Optimal)' : 'Full Speed'}
              </span>
            </div>
            <input
              type="range"
              min="11.0"
              max="15.0"
              step="0.5"
              value={speedKnots}
              onChange={(e) => setSpeedKnots(Number(e.target.value))}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 mt-1">
              <span>11.0 Kn (Eco)</span>
              <span>13.5 Kn (Balanced)</span>
              <span>15.0 Kn (Full)</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              VLSFO Bunker Price ($/MT):
            </label>
            <input
              type="number"
              value={bunkerPrice}
              onChange={(e) => setBunkerPrice(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
            />
          </div>

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500">Charter Hire Rate:</span>
              <span className="font-bold text-slate-800">${charterRatePerDay.toLocaleString()} / day</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Fixed Port Tariffs:</span>
              <span className="font-bold text-slate-800">${portDues.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Distance to Run:</span>
              <span className="font-bold text-slate-800">{distanceNm.toLocaleString()} NM</span>
            </div>
          </div>
        </div>

        {/* Right 2 Cols: Trade-off Outputs */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Fuel className="w-4 h-4 text-amber-500" />
              <h3 className="text-sm font-black text-slate-900">Optimization Results & Cost Breakdown</h3>
            </div>
            <span className="text-xs font-bold text-emerald-600 flex items-center gap-1">
              <Leaf className="w-3.5 h-3.5" />
              {co2EmissionsMt.toFixed(1)} MT CO₂
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Transit Time</span>
              <p className="text-base font-black text-slate-900 mt-0.5">{transitDays.toFixed(1)} Days</p>
              <p className="text-[10px] text-slate-500">+{portDays} days port ops</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Daily Burn</span>
              <p className="text-base font-black text-slate-900 mt-0.5">{dailyBurnMt.toFixed(1)} MT / d</p>
              <p className="text-[10px] text-slate-500">Total: {totalBunkerBurnMt.toFixed(0)} MT</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Bunker Cost</span>
              <p className="text-base font-black text-amber-600 mt-0.5">${(totalBunkerCost / 1000).toFixed(0)}k</p>
              <p className="text-[10px] text-slate-500">{((totalBunkerCost / totalVoyageCost) * 100).toFixed(0)}% of total</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Time Charter Cost</span>
              <p className="text-base font-black text-blue-600 mt-0.5">${(charterHireCost / 1000).toFixed(0)}k</p>
              <p className="text-[10px] text-slate-500">{((charterHireCost / totalVoyageCost) * 100).toFixed(0)}% of total</p>
            </div>
          </div>

          {/* Waypoint Sequence */}
          <div className="space-y-2 pt-2">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-700">
              Optimal Corridor Waypoints & Navigational Leg Breakdown:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-3 rounded-xl bg-blue-50/50 border border-blue-100">
                <span className="text-blue-600 font-bold text-[10px]">LEG 1 (DEPARTURE)</span>
                <p className="font-black text-slate-800">Balikpapan</p>
                <p className="text-[10px] text-slate-500">Lat: -1.26°, Lon: 116.83°</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 font-bold text-[10px]">LEG 2 (CHOKEPOINT)</span>
                <p className="font-black text-slate-800">Malacca Strait</p>
                <p className="text-[10px] text-slate-500">Transit check: Safe</p>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-slate-400 font-bold text-[10px]">LEG 3 (OPEN SEA)</span>
                <p className="font-black text-slate-800">Bay of Bengal</p>
                <p className="text-[10px] text-slate-500">Monsoon Factor: Low</p>
              </div>
              <div className="p-3 rounded-xl bg-emerald-50/50 border border-emerald-100">
                <span className="text-emerald-600 font-bold text-[10px]">LEG 4 (DESTINATION)</span>
                <p className="font-black text-slate-800">Paradip Port</p>
                <p className="text-[10px] text-slate-500">Berth: Bulk Terminal</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
