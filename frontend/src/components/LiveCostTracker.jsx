import React, { useState } from 'react';
import { DollarSign, Clock, Ship, CheckCircle2, TrendingUp, TrendingDown, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

export default function LiveCostTracker({ liveData, onBookNow }) {
  const [selectedClass, setSelectedClass] = useState('Supramax');
  const [charterType, setCharterType] = useState('voyage'); // 'voyage' | 'hire' | 'coa'
  const [bookingConfirmed, setBookingConfirmed] = useState(false);

  const rates = liveData?.freight_rates?.rates_by_class || {};
  const hireRates = liveData?.hire_rates || {};
  const weatherAdj = liveData?.freight_rates?.weather_adjustment_pct || 0;

  const currentClassData = rates[selectedClass] || { rate_usd_mt: 9.9, tce_usd_day: 11200, trend: 'stable' };
  const currentHireData = hireRates[selectedClass] || { day_rate_usd: 11200, monthly_usd: 336000, trend: 'stable' };

  // Example calculation for 55,000 MT voyage Indonesia -> Paradip (7.2 days)
  const cargoMt = 55000;
  const spotRate = currentClassData.rate_usd_mt;
  const freightTotal = spotRate * cargoMt;
  const bunkerEstimate = 26 * 7.2 * 620; // 26 mt/day * 7.2 days * $620
  const portCharges = currentHireData.day_rate_usd * 0.8;
  const totalVoyageCost = freightTotal + bunkerEstimate + portCharges;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between flex-wrap gap-2 bg-gradient-to-r from-slate-50 to-blue-50/30">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-600 text-white shadow-sm shadow-blue-600/30">
            <DollarSign className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-black text-slate-900 tracking-tight">
              Live Renting & Booking Cost Calculator
            </h3>
            <p className="text-[11px] text-slate-500 font-medium">
              Real-time daily hire, spot freight & COA charter rates
            </p>
          </div>
        </div>

        {weatherAdj > 0 && (
          <span className="bg-amber-100 text-amber-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full border border-amber-300">
            Weather Premium: +{weatherAdj}%
          </span>
        )}
      </div>

      {/* Vessel Class Selector Pills */}
      <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex flex-wrap gap-2">
        {['Handysize', 'Supramax', 'Panamax', 'Capesize'].map((vClass) => {
          const classRate = rates[vClass]?.rate_usd_mt || 9.9;
          const classHire = hireRates[vClass]?.day_rate_usd || 11200;
          const isSelected = selectedClass === vClass;

          return (
            <button
              key={vClass}
              onClick={() => setSelectedClass(vClass)}
              className={`flex-1 min-w-[130px] p-2.5 rounded-xl border text-left transition-all ${
                isSelected
                  ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-600/25'
                  : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'
              }`}
            >
              <div className={`text-[10px] font-black uppercase ${isSelected ? 'text-blue-100' : 'text-slate-500'}`}>
                {vClass}
              </div>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-sm font-black font-mono">${classRate.toFixed(2)}/MT</span>
                <span className={`text-[10px] font-bold ${isSelected ? 'text-blue-100' : 'text-slate-500'}`}>
                  ${(classHire / 1000).toFixed(1)}k/day
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Comparison Grid: Renting vs Booking */}
      <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Option 1: Renting (Time Charter Hire) */}
        <div
          onClick={() => setCharterType('hire')}
          className={`p-4 rounded-xl border transition-all cursor-pointer relative ${
            charterType === 'hire'
              ? 'border-blue-600 bg-blue-50/30 ring-2 ring-blue-500/20'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider text-slate-600">
              Option 1: Vessel Renting (Time Charter)
            </span>
            <span className="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded">
              Daily Hire
            </span>
          </div>

          <div className="mt-3">
            <div className="text-2xl font-black text-slate-900 font-mono">
              ${currentHireData.day_rate_usd?.toLocaleString()}{' '}
              <span className="text-xs font-bold text-slate-500">/ day</span>
            </div>
            <div className="text-xs font-bold text-slate-600 mt-0.5">
              ${(currentHireData.monthly_usd / 1000)?.toFixed(0)}k / month commitment
            </div>
          </div>

          <ul className="mt-3 space-y-1.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
              <span>Full operational scheduling flexibility</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
              <span>Charterer pays bunkers & port disbursement</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
              <span>Best for consecutive 3 to 6-month continuous trades</span>
            </li>
          </ul>
        </div>

        {/* Option 2: Booking (Single Voyage Spot) */}
        <div
          onClick={() => setCharterType('voyage')}
          className={`p-4 rounded-xl border transition-all cursor-pointer relative ${
            charterType === 'voyage'
              ? 'border-emerald-600 bg-emerald-50/30 ring-2 ring-emerald-500/20'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider text-slate-600">
              Option 2: Voyage Booking (Spot Fixture)
            </span>
            <span className="bg-emerald-100 text-emerald-800 text-[10px] font-black px-2 py-0.5 rounded">
              Pay Per MT
            </span>
          </div>

          <div className="mt-3">
            <div className="text-2xl font-black text-emerald-700 font-mono">
              ${spotRate.toFixed(2)}{' '}
              <span className="text-xs font-bold text-slate-500">/ MT</span>
            </div>
            <div className="text-xs font-bold text-slate-600 mt-0.5">
              Estimated Landed Cost: ${(totalVoyageCost / 1e6).toFixed(2)}M (55,000 MT)
            </div>
          </div>

          <ul className="mt-3 space-y-1.5 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Zero forward volume commitment</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Shipowner bears bunker price and voyage risks</span>
            </li>
            <li className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Recommended when freight rates are expected to soften</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Booking Confirmation / Action Bar */}
      <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="text-xs text-slate-600">
          Selected: <strong className="text-slate-900">{selectedClass}</strong> vessel via{' '}
          <strong className="text-slate-900 uppercase">
            {charterType === 'hire' ? 'Time Charter (Renting)' : 'Spot Voyage Booking'}
          </strong>
        </div>

        <div className="flex items-center gap-3">
          {bookingConfirmed && (
            <span className="text-xs font-bold text-emerald-600 flex items-center gap-1">
              <CheckCircle2 className="w-4 h-4" /> Fixture Request Logged!
            </span>
          )}

          <button
            onClick={() => {
              setBookingConfirmed(true);
              setTimeout(() => setBookingConfirmed(false), 4000);
              if (onBookNow) onBookNow(selectedClass, charterType);
            }}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-xs rounded-xl shadow-md shadow-blue-500/20 transition-all flex items-center gap-2 active:scale-95"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate Booking Term Sheet</span>
          </button>
        </div>
      </div>
    </div>
  );
}
