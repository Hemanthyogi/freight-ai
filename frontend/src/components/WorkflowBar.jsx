import React from 'react';
import { ArrowRight, Waves } from 'lucide-react';

export default function WorkflowBar() {
  const steps = ['FORECAST', 'EVALUATE', 'OPTIMIZE', 'RECOMMEND'];

  return (
    <footer className="mt-4 bg-white border border-slate-200 rounded-xl p-3 shadow-sm flex flex-wrap items-center justify-between gap-4">
      {/* Workflow Step Indicator */}
      <div className="flex items-center gap-2">
        {steps.map((step, idx) => {
          const isLast = idx === steps.length - 1;
          return (
            <React.Fragment key={step}>
              <div
                className={`px-3 py-1 rounded-md text-[11px] font-black tracking-wider ${
                  isLast
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-700'
                }`}
              >
                {step}
              </div>
              {!isLast && <ArrowRight className="w-3.5 h-3.5 text-slate-400" />}
            </React.Fragment>
          );
        })}
      </div>

      {/* Center Subtext */}
      <div className="text-xs text-slate-500 font-medium hidden lg:block">
        AI-assisted decision support for cost-efficient, risk-aware vessel chartering.
      </div>

      {/* Right National / Maritime Slogan */}
      <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
        <Waves className="w-4 h-4 text-blue-600" />
        <span>Safer Ocean · Stronger Economy · Prosperous India</span>
      </div>
    </footer>
  );
}
