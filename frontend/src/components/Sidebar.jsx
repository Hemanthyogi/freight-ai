import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Ship,
  Anchor,
  Box,
  Compass,
  GitCompare,
  FileText
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'forecast', label: 'Freight Forecast', icon: TrendingUp },
    { id: 'vessel', label: 'Vessel Matching', icon: Ship },
    { id: 'port', label: 'Port Feasibility', icon: Anchor },
    { id: 'cargo', label: 'Cargo Procurement', icon: Box },
    { id: 'optimization', label: 'Optimization', icon: Compass },
    { id: 'scenarios', label: 'Scenario Analysis', icon: GitCompare },
    { id: 'reports', label: 'Reports', icon: FileText },
  ];

  return (
    <aside className="w-64 bg-[#0a1931] text-slate-300 flex flex-col justify-between shrink-0 min-h-screen border-r border-[#152e53]">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-[#152e53]/60 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Ship className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white tracking-wide">
              FREIGHTMIND <span className="text-blue-400">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 tracking-tight">Smarter Routes. Stronger Tomorrow.</p>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'text-slate-300 hover:bg-[#13284a] hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Decorative Bottom Graphic */}
      <div className="p-4 m-3 rounded-xl bg-gradient-to-t from-[#061224] to-[#0d2347] border border-blue-900/40 relative overflow-hidden">
        <div className="relative z-10">
          <p className="text-[10px] font-bold text-blue-300 uppercase tracking-wider">CLEAN SEAS</p>
          <p className="text-[11px] font-extrabold text-white uppercase tracking-wider">STRONGER TRADE</p>
          <p className="text-[10px] font-bold text-blue-400 uppercase tracking-wider">BRIGHTER INDIA</p>
        </div>
        <Ship className="w-20 h-20 text-blue-500/10 absolute -right-3 -bottom-3 transform -rotate-12 pointer-events-none" />
      </div>
    </aside>
  );
}
