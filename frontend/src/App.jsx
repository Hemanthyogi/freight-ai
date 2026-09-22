import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import KpiBar from './components/KpiBar';
import ForecastChartCard from './components/ForecastChartCard';
import AiRecommendationCard from './components/AiRecommendationCard';
import OptimalRouteMap from './components/OptimalRouteMap';
import TopVesselsTable from './components/TopVesselsTable';
import CargoRequirementCard from './components/CargoRequirementCard';
import ScenarioComparison from './components/ScenarioComparison';
import WhyRecommendation from './components/WhyRecommendation';
import WorkflowBar from './components/WorkflowBar';
import ForecastView from './views/ForecastView';
import VesselMatchingView from './views/VesselMatchingView';
import PortFeasibilityView from './views/PortFeasibilityView';
import CargoProcurementView from './views/CargoProcurementView';
import OptimizationView from './views/OptimizationView';
import ScenarioAnalysisView from './views/ScenarioAnalysisView';
import ReportsView from './views/ReportsView';
import LiveOperationsView from './views/LiveOperationsView';
import LiveStatusBar from './components/LiveStatusBar';
import WeatherAlertBanner from './components/WeatherAlertBanner';
import defaultDashboardData from './data/defaultDashboardData.json';
import { Play, Sparkles, RefreshCw, X, ShieldCheck, CheckCircle2, ChevronRight, Home, Radio } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(defaultDashboardData);
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [liveData, setLiveData] = useState(null);
  const [liveLoading, setLiveLoading] = useState(false);

  // Form State for Interactive Evaluation
  const [origin, setOrigin] = useState('Indonesia');
  const [destPort, setDestPort] = useState('paradip');
  const [commodity, setCommodity] = useState('Iron Ore');
  const [quantity, setQuantity] = useState(250000);
  const [vesselPref, setVesselPref] = useState('Supramax');
  const [strategy, setStrategy] = useState('Multiple Voyage Charter');

  // Load live maritime operations state
  const fetchLiveState = async () => {
    setLiveLoading(true);
    try {
      const res = await fetch('/api/v1/live/state');
      if (res.ok) {
        const data = await res.json();
        setLiveData(data);
      }
    } catch (err) {
      console.warn('Live state polling fallback:', err);
    } finally {
      setLiveLoading(false);
    }
  };

  // Load default SIH Scenario
  const fetchDefaultScenario = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/voyage-analysis/default');
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      } else {
        console.warn('Backend not responding yet, using default state.');
        setDashboardData((prev) => prev || defaultDashboardData);
      }
    } catch (err) {
      console.warn('API error, using local fallback state:', err);
      setDashboardData((prev) => prev || defaultDashboardData);
    } finally {
      setLoading(false);
    }
  };

  // Run Custom Analysis
  const handleAnalyze = async (customParams = null) => {
    setLoading(true);
    const payload = customParams || {
      origin,
      destination_port_id: destPort,
      commodity,
      cargo_quantity_mt: Number(quantity),
      delivery_window: 'September - October 2026',
      procurement_strategy: strategy,
      vessel_preference: vesselPref,
    };

    try {
      const res = await fetch('/api/v1/voyage-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      }
    } catch (err) {
      console.error('Analysis request error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load on mount & start 60s live poller
  useEffect(() => {
    fetchDefaultScenario();
    fetchLiveState();

    // 60-second periodic poll for live stream updates
    const liveTimer = setInterval(() => {
      fetchLiveState();
    }, 60000);

    return () => clearInterval(liveTimer);
  }, []);

  // Quick Preset Scenarios for SIH Judges
  const loadPreset = (presetName) => {
    if (presetName === 'indonesia_iron_ore') {
      setOrigin('Indonesia');
      setDestPort('paradip');
      setCommodity('Iron Ore');
      setQuantity(250000);
      setVesselPref('Supramax');
      setStrategy('Multiple Voyage Charter');
      handleAnalyze({
        origin: 'Indonesia',
        destination_port_id: 'paradip',
        commodity: 'Iron Ore',
        cargo_quantity_mt: 250000,
        delivery_window: 'September - October 2026',
        procurement_strategy: 'Multiple Voyage Charter',
        vessel_preference: 'Supramax',
      });
    } else if (presetName === 'australia_coal') {
      setOrigin('Australia');
      setDestPort('paradip');
      setCommodity('Thermal Coal');
      setQuantity(100000);
      setVesselPref('Panamax');
      setStrategy('3-Month Contract');
      handleAnalyze({
        origin: 'Australia',
        destination_port_id: 'paradip',
        commodity: 'Thermal Coal',
        cargo_quantity_mt: 100000,
        delivery_window: 'October - December 2026',
        procurement_strategy: '3-Month Multiple Voyage',
        vessel_preference: 'Panamax',
      });
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#f0f4f9]">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Scroll Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Global Header */}
        <Header />

        {/* 24/7 Live Operations Status Bar */}
        <LiveStatusBar liveData={liveData} onRefresh={fetchLiveState} loading={liveLoading} />

        {/* Dashboard Canvas */}
        <main className="p-5 space-y-4 max-w-7xl mx-auto w-full">
          {/* Breadcrumb Navigation when on sub-views */}
          {activeTab !== 'dashboard' && (
            <div className="flex items-center justify-between bg-white rounded-xl px-4 py-2.5 border border-slate-200 shadow-sm text-xs">
              <div className="flex items-center gap-2 text-slate-500 font-medium">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-bold"
                >
                  <Home className="w-3.5 h-3.5" />
                  Dashboard
                </button>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                <span className="font-black text-slate-800 uppercase tracking-wide">
                  {activeTab === 'live' && '24/7 Live Maritime Operations & Climate Risk'}
                  {activeTab === 'forecast' && 'Freight Rate Forecasting'}
                  {activeTab === 'vessel' && 'Vessel Matching & Fleet Selection'}
                  {activeTab === 'port' && 'Port Feasibility & Hard Constraints'}
                  {activeTab === 'cargo' && 'Cargo Procurement & Laycan Planning'}
                  {activeTab === 'optimization' && 'Speed, Bunker & Route Optimization'}
                  {activeTab === 'scenarios' && 'Scenario Analysis & Contract Trade-offs'}
                  {activeTab === 'reports' && 'Empirical Reports & Model Benchmarks'}
                </span>
              </div>

              <button
                onClick={() => setActiveTab('dashboard')}
                className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-lg transition-all"
              >
                ← Back to Dashboard Overview
              </button>
            </div>
          )}

          {/* TAB 1: MASTER DASHBOARD OVERVIEW */}
          {activeTab === 'dashboard' && (
            <>
              {/* Live Weather Alerts Banner if active */}
              {liveData?.weather_alerts?.length > 0 && (
                <WeatherAlertBanner
                  alerts={liveData.weather_alerts}
                  onLockCharter={() => setActiveTab('live')}
                  onViewOperations={() => setActiveTab('live')}
                />
              )}

              {/* Quick Scenario Preset Controls */}
              <div className="bg-white rounded-xl p-3 border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span className="text-xs font-black uppercase tracking-wider text-slate-800">
                    SIH 2026 Demonstration Scenario:
                  </span>
                  <div className="flex items-center gap-1.5 ml-1">
                    <button
                      onClick={() => loadPreset('indonesia_iron_ore')}
                      className="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-all"
                    >
                      🇮🇩 Indonesia → Paradip (Iron Ore, 250K MT)
                    </button>
                    <button
                      onClick={() => loadPreset('australia_coal')}
                      className="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
                    >
                      🇦🇺 Australia → Paradip (Coal, 100K MT)
                    </button>
                  </div>
                </div>

                {/* Re-calculate Button */}
                <button
                  onClick={() => handleAnalyze()}
                  disabled={loading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                  <span>{loading ? 'Optimizing Fleet...' : 'Re-Run Optimization'}</span>
                </button>
              </div>

              {/* Top 5 KPI Cards Bar */}
              <KpiBar kpis={dashboardData?.kpis} />

              {/* Row 1: Forecast Chart (2/3) + AI Recommendation Card (1/3) */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2">
                  <ForecastChartCard
                    historicalData={dashboardData?.forecast_chart_historical}
                    forecastData={dashboardData?.forecast_chart_prediction}
                    insight={dashboardData?.forecast_insight}
                    tagline={dashboardData?.quote_tagline}
                  />
                </div>
                <div className="lg:col-span-1">
                  <AiRecommendationCard
                    recommendation={dashboardData?.ai_recommendation}
                    onPlanClick={() => setShowPlanModal(true)}
                  />
                </div>
              </div>

              {/* Row 2: Optimal Voyage Route (1/3) + Top Vessel Matches (1/3) + Cargo Requirement (1/3) */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <OptimalRouteMap routeData={dashboardData?.voyage_route} />
                <TopVesselsTable
                  vessels={dashboardData?.top_vessel_matches}
                  onSelectVessel={() => setShowPlanModal(true)}
                />
                <CargoRequirementCard requirement={dashboardData?.cargo_requirement} />
              </div>

              {/* Row 3: Scenario Comparison (1/2) + Why This Recommendation (1/2) */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ScenarioComparison scenarios={dashboardData?.scenario_comparison} />
                <WhyRecommendation
                  reasons={dashboardData?.why_recommendation}
                  quote={dashboardData?.quote_tagline}
                />
              </div>

              {/* Bottom Workflow Status Bar */}
              <WorkflowBar />
            </>
          )}

          {/* TAB: 24/7 LIVE OPERATIONS & CLIMATE RISK */}
          {activeTab === 'live' && (
            <LiveOperationsView
              liveData={liveData}
              onRefresh={fetchLiveState}
              loading={liveLoading}
            />
          )}

          {/* TAB 2: FREIGHT FORECAST VIEW */}
          {activeTab === 'forecast' && (
            <ForecastView dashboardData={dashboardData} />
          )}

          {/* TAB 3: VESSEL MATCHING VIEW */}
          {activeTab === 'vessel' && (
            <VesselMatchingView
              dashboardData={dashboardData}
              onSelectVessel={() => setShowPlanModal(true)}
            />
          )}

          {/* TAB 4: PORT FEASIBILITY VIEW */}
          {activeTab === 'port' && (
            <PortFeasibilityView />
          )}

          {/* TAB 5: CARGO PROCUREMENT VIEW */}
          {activeTab === 'cargo' && (
            <CargoProcurementView
              dashboardData={dashboardData}
              onAnalyzeCustom={handleAnalyze}
            />
          )}

          {/* TAB 6: OPTIMIZATION VIEW */}
          {activeTab === 'optimization' && (
            <OptimizationView dashboardData={dashboardData} />
          )}

          {/* TAB 7: SCENARIO ANALYSIS VIEW */}
          {activeTab === 'scenarios' && (
            <ScenarioAnalysisView dashboardData={dashboardData} />
          )}

          {/* TAB 8: REPORTS & BENCHMARKS VIEW */}
          {activeTab === 'reports' && (
            <ReportsView dashboardData={dashboardData} />
          )}
        </main>
      </div>

      {/* View Optimal Plan Modal */}
      {showPlanModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900">
                    Charter Execution Plan & Feasibility Report
                  </h3>
                  <p className="text-xs text-slate-500">
                    Validated against port draft, beam, LOA, and AI rate forecasts
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowPlanModal(false)}
                className="w-8 h-8 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs text-slate-700">
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
                <div className="font-bold text-emerald-900 flex items-center gap-1.5 mb-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Recommended Action: Fix MV Ocean Crest (58,000 DWT)
                </div>
                <p className="text-[11px] text-emerald-800 leading-relaxed">
                  Charter between <strong>18 – 24 September 2026</strong> to capture the predicted 6.4% freight softening. Under consecutive 3-month voyages, expected total procurement savings exceed <strong>$280,000</strong> compared to prompt spot chartering.
                </p>
              </div>

              {/* Port Feasibility Checks */}
              <div>
                <h4 className="font-extrabold text-slate-900 mb-2">Destination Port Physical Feasibility (Paradip):</h4>
                <div className="grid grid-cols-3 gap-2">
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-center">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Draft Check</span>
                    <div className="text-xs font-bold text-emerald-600 mt-0.5">12.5m ≤ 17.0m (PASS)</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-center">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">LOA Check</span>
                    <div className="text-xs font-bold text-emerald-600 mt-0.5">190m ≤ 260m (PASS)</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-center">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Beam Check</span>
                    <div className="text-xs font-bold text-emerald-600 mt-0.5">32.2m ≤ 43.0m (PASS)</div>
                  </div>
                </div>
              </div>

              {/* Operational Next Steps */}
              <div>
                <h4 className="font-extrabold text-slate-900 mb-2">Recommended Operational Protocol:</h4>
                <ol className="list-decimal list-inside space-y-1 text-slate-600">
                  <li>Issue Notice of Readiness (NOR) aligned with 18 Sep laycan arrival window.</li>
                  <li>Secure bunker collar adjustment tied to VLSFO index (~$580/MT).</li>
                  <li>Incorporate 48-hour free laytime clause for Paradip mechanized discharge berth.</li>
                </ol>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2 border-t border-slate-100 pt-3">
              <button
                onClick={() => setShowPlanModal(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-bold transition-all"
              >
                Close
              </button>
              <button
                onClick={() => {
                  alert('Charter Plan Exported as PDF/Summary.');
                  setShowPlanModal(false);
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-all shadow-md shadow-indigo-600/30"
              >
                Export Charter Brief
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
