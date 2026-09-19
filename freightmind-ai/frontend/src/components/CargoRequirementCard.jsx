import React from 'react';
import { Box, Layers, MapPin, Navigation, Calendar, FileText } from 'lucide-react';

export default function CargoRequirementCard({ requirement }) {
  const req = requirement || {
    commodity: 'Iron Ore',
    required_quantity_mt: '250,000 MT',
    origin: 'Indonesia',
    destination: 'East Coast India',
    delivery_window: 'September - October 2026',
    procurement_strategy: 'Multiple Voyage Charter',
  };

  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <Box className="w-5 h-5 text-blue-600" />
        <h2 className="text-xs font-black uppercase tracking-wider text-slate-800">
          BULK CARGO REQUIREMENT
        </h2>
      </div>

      {/* Details Grid */}
      <div className="space-y-2.5 text-xs">
        {/* Commodity & Quantity */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">COMMODITY</div>
              <div className="font-bold text-slate-900">{req.commodity}</div>
            </div>
          </div>
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <Box className="w-4 h-4 text-indigo-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">REQUIRED QUANTITY</div>
              <div className="font-bold text-slate-900">{req.required_quantity_mt}</div>
            </div>
          </div>
        </div>

        {/* Origin & Destination */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-amber-500 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">ORIGIN</div>
              <div className="font-bold text-slate-900">{req.origin}</div>
            </div>
          </div>
          <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
            <Navigation className="w-4 h-4 text-emerald-600 shrink-0" />
            <div>
              <div className="text-[9px] font-bold uppercase text-slate-400">DESTINATION</div>
              <div className="font-bold text-slate-900">{req.destination}</div>
            </div>
          </div>
        </div>

        {/* Delivery Window */}
        <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-600 shrink-0" />
          <div>
            <div className="text-[9px] font-bold uppercase text-slate-400">DELIVERY WINDOW</div>
            <div className="font-bold text-slate-900">{req.delivery_window}</div>
          </div>
        </div>

        {/* Procurement Strategy */}
        <div className="p-2 rounded-lg bg-blue-50/70 border border-blue-100 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600 shrink-0" />
          <div>
            <div className="text-[9px] font-bold uppercase text-blue-700">PROCUREMENT STRATEGY</div>
            <div className="font-bold text-blue-900">{req.procurement_strategy}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
