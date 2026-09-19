import React, { useState } from 'react';
import {
  Box,
  TrendingDown,
  Calendar,
  Layers,
  DollarSign,
  PackageCheck,
  Ship,
  ArrowRight,
  ShieldAlert,
  Percent,
  Calculator,
  CheckCircle2
} from 'lucide-react';

export default function CargoProcurementView({ dashboardData, onAnalyzeCustom }) {
  const [commodity, setCommodity] = useState('Iron Ore');
  const [totalQty, setTotalQty] = useState(250000);
  const [origin, setOrigin] = useState('Indonesia');
  const [destination, setDestination] = useState('paradip');
  const [fobPrice, setFobPrice] = useState(105); // $/MT FOB
  const [freightRate, setFreightRate] = useState(9.90); // $/MT Freight

  const parcelSize = 58000; // Supramax standard parcel
  const numberOfVoyages = Math.ceil(totalQty / parcelSize);
  const laycanSpacingDays = 18;

  // Landed Cost Calculations
  const cargoCostTotal = totalQty * fobPrice;
  const freightCostTotal = totalQty * freightRate;
  const portTariffEst = numberOfVoyages * 35000;
  const insuranceEst = cargoCostTotal * 0.0035;
  const totalLandedCost = cargoCostTotal + freightCostTotal + portTariffEst + insuranceEst;
  const landedPerMt = totalLandedCost / totalQty;

  const commodities = [
    { name: 'Iron Ore', defaultFob: 105, origin: 'Indonesia', unit: 'MT' },
    { name: 'Thermal Coal', defaultFob: 112, origin: 'Indonesia / Australia', unit: 'MT' },
    { name: 'Coking Coal', defaultFob: 220, origin: 'Australia', unit: 'MT' },
    { name: 'Bauxite', defaultFob: 58, origin: 'Australia / Guinea', unit: 'MT' },
    { name: 'Limestone', defaultFob: 35, origin: 'UAE / Oman', unit: 'MT' },
  ];

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0a1931] via-[#102a54] to-[#0a1931] rounded-2xl p-6 text-white border border-blue-900/50 shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                Bulk Cargo Procurement Engine
              </span>
              <span className="text-xs text-slate-400">Total Procurement Horizon: 3-Month Multi-Voyage Program</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
              <Box className="w-6 h-6 text-blue-400" />
              Cargo Procurement & Laycan Scheduling
            </h2>
            <p className="text-xs text-slate-300 max-w-2xl mt-1">
              Synchronizes overseas commodity purchasing with maritime freight chartering. Optimizes parcel sizes, laycan intervals, and landed CIF costs for steel and power plants on India's East Coast.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-white/5 backdrop-blur-sm p-3 rounded-xl border border-white/10">
            <div className="text-right">
              <p className="text-[10px] uppercase font-bold text-slate-400">Est. Landed Cost (CIF)</p>
              <p className="text-2xl font-black text-white">${landedPerMt.toFixed(2)} <span className="text-xs font-medium text-slate-300">/ MT</span></p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-blue-600/30 flex items-center justify-center text-blue-300">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Controls & Parcel Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left 2 Cols: Procurement Parameters */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Calculator className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-black text-slate-900">Procurement Specifications & Pricing Parameters</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Bulk Commodity:
              </label>
              <select
                value={commodity}
                onChange={(e) => {
                  const comm = commodities.find((c) => c.name === e.target.value);
                  setCommodity(e.target.value);
                  if (comm) setFobPrice(comm.defaultFob);
                }}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
              >
                {commodities.map((c) => (
                  <option key={c.name} value={c.name}>{c.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Total Required Volume (MT):
              </label>
              <input
                type="number"
                step="10000"
                value={totalQty}
                onChange={(e) => setTotalQty(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                FOB Commodity Price ($/MT):
              </label>
              <input
                type="number"
                step="1"
                value={fobPrice}
                onChange={(e) => setFobPrice(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Target Freight Rate ($/MT):
              </label>
              <input
                type="number"
                step="0.1"
                value={freightRate}
                onChange={(e) => setFreightRate(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
              />
            </div>
          </div>

          {/* Quick Volume Chips */}
          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Quick Volume Presets:
            </label>
            <div className="flex flex-wrap gap-2">
              {[50000, 100000, 150000, 250000, 500000].map((v) => (
                <button
                  key={v}
                  onClick={() => setTotalQty(v)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition-all ${
                    totalQty === v
                      ? 'bg-blue-50 border-blue-300 text-blue-700'
                      : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {(v / 1000).toFixed(0)}k MT
                </button>
              ))}
            </div>
          </div>

          {/* Parcel Split Summary */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
            <h4 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <PackageCheck className="w-4 h-4 text-blue-600" />
              Automated Parcel Split & Sequencing Plan
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Total Voyages</span>
                <p className="text-base font-black text-slate-900 mt-0.5">{numberOfVoyages} Consecutive</p>
              </div>
              <div className="p-2.5 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Parcel Size</span>
                <p className="text-base font-black text-slate-900 mt-0.5">~{Math.round(totalQty / numberOfVoyages).toLocaleString()} MT</p>
              </div>
              <div className="p-2.5 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Laycan Interval</span>
                <p className="text-base font-black text-slate-900 mt-0.5">Every {laycanSpacingDays} Days</p>
              </div>
              <div className="p-2.5 bg-white rounded-lg border border-slate-100">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Stockout Risk</span>
                <p className="text-base font-black text-emerald-600 mt-0.5">MINIMAL</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Col: CIF Cost Waterfall */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3 mb-3">
              <DollarSign className="w-4 h-4 text-emerald-600" />
              <h3 className="text-sm font-black text-slate-900">Total CIF Landed Cost Waterfall</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">FOB Commodity Value:</span>
                <span className="font-bold text-slate-900">${(cargoCostTotal / 1e6).toFixed(2)}M</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Ocean Freight ({totalQty.toLocaleString()} MT):</span>
                <span className="font-bold text-blue-600">${(freightCostTotal / 1e6).toFixed(2)}M</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Port Tariffs & Pilotage ({numberOfVoyages} calls):</span>
                <span className="font-bold text-slate-900">${(portTariffEst / 1000).toFixed(0)}k</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Marine Cargo Insurance (0.35%):</span>
                <span className="font-bold text-slate-900">${(insuranceEst / 1000).toFixed(0)}k</span>
              </div>

              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 mt-2">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-xs font-black text-emerald-900 uppercase tracking-wide">Total CIF Landed:</span>
                    <p className="text-xl font-black text-emerald-900">${(totalLandedCost / 1e6).toFixed(2)}M</p>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-emerald-700 uppercase font-bold">Landed Unit Rate:</span>
                    <p className="text-base font-black text-emerald-900">${landedPerMt.toFixed(2)} / MT</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 text-xs text-slate-500 space-y-1">
            <p className="flex items-center gap-1.5 text-emerald-700 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Volume commitment discount of ~3% applied across multi-voyage contract.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
