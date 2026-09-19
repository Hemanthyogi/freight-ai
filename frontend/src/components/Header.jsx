import React from 'react';
import { BrainCircuit, Award } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between shadow-sm">
      {/* Title & Slogan */}
      <div className="flex items-center gap-3.5">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <BrainCircuit className="w-7 h-7" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-black text-slate-900 tracking-tight">FREIGHTMIND AI</h1>
            <span className="bg-blue-50 text-blue-700 text-[11px] font-bold px-2 py-0.5 rounded-full border border-blue-200">
              Prototype
            </span>
          </div>
          <p className="text-xs font-semibold text-slate-700">
            Intelligent Freight Forecasting & Vessel Charter Optimization
          </p>
          <p className="text-[11px] text-slate-500 font-medium">
            Data-Driven Decisions for a Resilient Maritime Supply Chain
          </p>
        </div>
      </div>

      {/* SIH 2026 Badges */}
      <div className="flex items-center gap-5">
        <div className="text-right border-r border-slate-200 pr-5">
          <div className="text-base font-black text-slate-900 tracking-tight">PS 26006</div>
          <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
            SIH 2026 — Problem Statement
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-full bg-emerald-50 border border-emerald-300 flex items-center justify-center text-emerald-700 font-bold">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs font-black text-slate-900 leading-tight">SMART INDIA HACKATHON 2026</div>
            <div className="text-[10px] font-medium text-slate-500">Innovate · Solve · Build for a Better India</div>
          </div>
        </div>
      </div>
    </header>
  );
}
