import React, { useState } from 'react';
import { Sparkles, AlertCircle, Info, CheckCircle2, ChevronRight, ArrowUpRight, Zap, ShieldAlert } from 'lucide-react';

export default function AISuggestionsPanel({ suggestions, onAction, onRefresh }) {
  const [filter, setFilter] = useState('ALL');

  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm text-center">
        <Sparkles className="w-6 h-6 text-indigo-400 mx-auto mb-2 animate-bounce" />
        <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider">AI Suggestions Engine</h4>
        <p className="text-xs text-slate-500 mt-1">Analyzing live market feeds and maritime weather...</p>
      </div>
    );
  }

  const filtered = suggestions.filter((s) => {
    if (filter === 'ALERTS') return s.severity === 'CRITICAL' || s.severity === 'HIGH' || s.severity === 'MEDIUM';
    if (filter === 'INSIGHTS') return s.severity === 'INFO' || s.severity === 'LOW';
    return true;
  });

  const severityConfig = {
    CRITICAL: {
      badge: 'bg-rose-50 text-rose-700 border-rose-200',
      border: 'border-l-rose-500',
      icon: ShieldAlert,
      iconColor: 'text-rose-600',
    },
    HIGH: {
      badge: 'bg-orange-50 text-orange-700 border-orange-200',
      border: 'border-l-orange-500',
      icon: AlertCircle,
      iconColor: 'text-orange-600',
    },
    MEDIUM: {
      badge: 'bg-amber-50 text-amber-700 border-amber-200',
      border: 'border-l-amber-500',
      icon: Zap,
      iconColor: 'text-amber-600',
    },
    INFO: {
      badge: 'bg-blue-50 text-blue-700 border-blue-200',
      border: 'border-l-blue-500',
      icon: Info,
      iconColor: 'text-blue-600',
    },
    LOW: {
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      border: 'border-l-emerald-500',
      icon: CheckCircle2,
      iconColor: 'text-emerald-600',
    },
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between flex-wrap gap-2 bg-gradient-to-r from-slate-50 to-indigo-50/30">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-600 text-white shadow-sm shadow-indigo-600/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-black text-slate-900 tracking-tight flex items-center gap-2">
              Proactive AI Decision Center
              <span className="text-[10px] font-bold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
                {suggestions.length} Active
              </span>
            </h3>
            <p className="text-[11px] text-slate-500 font-medium">Real-time voyage optimization & risk mitigation signals</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg text-[11px] font-bold">
          {['ALL', 'ALERTS', 'INSIGHTS'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2.5 py-1 rounded-md transition-all ${
                filter === f
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Suggestion Cards List */}
      <div className="p-3 space-y-2.5 max-h-[380px] overflow-y-auto">
        {filtered.map((item) => {
          const cfg = severityConfig[item.severity] || severityConfig.INFO;
          const Icon = cfg.icon;

          return (
            <div
              key={item.id}
              className={`p-3 rounded-xl border border-slate-200 border-l-4 ${cfg.border} bg-white hover:bg-slate-50/80 transition-all shadow-xs`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5">
                  <Icon className={`w-4 h-4 ${cfg.iconColor} shrink-0 mt-0.5`} />
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded border ${cfg.badge}`}>
                        {item.severity}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900 leading-snug">{item.title}</h4>
                    </div>
                    <p className="text-[11px] text-slate-600 mt-1 leading-relaxed font-medium">{item.message}</p>
                  </div>
                </div>

                {item.action && (
                  <button
                    onClick={() => onAction && onAction(item.action)}
                    className="shrink-0 flex items-center gap-1 text-[11px] font-extrabold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1.5 rounded-lg transition-all"
                  >
                    <span>{item.action_label || 'Act'}</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
