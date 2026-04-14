import { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Activity, TrendingUp, Users, Settings, 
  Zap, Heart, Database, Radio, ShieldAlert
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- TYPES ---

interface Agent {
  id: string;
  money: number;
  food: number;
  alive: boolean;
  reward?: number;
  action?: string;
  persona?: string;
  logs?: any[];
}

interface MarketData {
  food: number;
  energy: number;
  materials: number;
}

interface AnalyticsData {
  gini: number;
  volatility: number;
  market_status: string;
  survival_rate: number;
  wealth_distribution: number[];
}

interface SimPayload {
  step: number;
  market: MarketData;
  analytics: AnalyticsData;
  agents: Agent[];
  history: any[];
}

// --- NEXUS COMPONENTS ---

const NexusHeader = ({ step, isRunning, toggleSim }: any) => (
    <div className="fixed top-0 left-0 right-0 z-50 px-12 py-8 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent backdrop-blur-[2px]">
        <div className="flex items-center gap-6">
            <div className="w-12 h-12 rounded-2xl bg-[#1a1a1a] border border-white/10 flex items-center justify-center shadow-2xl overflow-hidden p-1">
                <img src="/img/L1.png" alt="Logo" className="w-full h-full object-contain" />
            </div>
            <div className="flex flex-col">
                <span className="text-xl font-display font-bold tracking-tight text-white">AetherMarket</span>
                <span className="text-[10px] font-bold opacity-30 tracking-[0.2em] uppercase">Status: Nominal / Cycle {step}</span>
            </div>
        </div>

        <div className="flex items-center gap-4">
             <div className="bg-white/5 border border-white/5 rounded-2xl px-6 py-2 flex items-center gap-4">
                <div className={cn("w-2 h-2 rounded-full", isRunning ? "bg-[#9d4edd] animate-pulse" : "bg-white/20")} />
                <span className="text-[10px] font-black uppercase tracking-widest opacity-60">System_{isRunning ? 'Active' : 'Standby'}</span>
                <button onClick={toggleSim} className="ml-4 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-[#9d4edd] hover:text-black transition-all">
                    {isRunning ? <Zap size={14} fill="currentColor" /> : <Radio size={14} />}
                </button>
             </div>
        </div>
    </div>
);

const NexusNav = () => {
    const loc = useLocation();
    return (
        <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-50 bg-[#111]/80 backdrop-blur-3xl border border-white/5 rounded-3xl px-8 flex items-center gap-10 shadow-2xl p-2">
            {[
                { label: 'Overview', path: '/', icon: Activity },
                { label: 'Analysis', path: '/analysis', icon: Database },
                { label: 'Flux', path: '/market', icon: TrendingUp },
                { label: 'Roster', path: '/agents', icon: Users },
                { label: 'Engine', path: '/config', icon: Settings }
            ].map((item) => (
                <Link 
                    key={item.path} 
                    to={item.path}
                    className={cn(
                        "flex items-center gap-3 px-6 py-3 rounded-2xl transition-all font-medium text-xs",
                        loc.pathname === item.path ? "bg-[#9d4edd] text-black shadow-[0_10px_30px_rgba(157,78,221,0.3)]" : "text-white/40 hover:text-white"
                    )}
                >
                    <item.icon size={16} />
                    <span className="hidden lg:inline">{item.label}</span>
                </Link>
            ))}
        </div>
    );
};

// --- PAGES ---

const NexusOverview = ({ data }: any) => {
    const totalWealth = data?.agents.reduce((acc: number, a: Agent) => acc + (a.money || 0), 0) || 0;
    const aliveCount = data?.agents.filter((a: Agent) => a.alive).length || 0;
    const gini = data?.analytics?.gini || 0;

    return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="pt-40 px-12 h-screen overflow-y-auto custom-scrollbar pb-32">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div className="nexus-card flex flex-col justify-center items-center text-center py-20 bg-gradient-to-br from-[#111] to-[#0a0a0a] group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-6">
                        <span className={cn(
                            "text-[8px] font-black px-3 py-1 rounded-full border tracking-widest uppercase",
                            data?.analytics?.market_status === 'CRASH' ? "bg-red-500/20 text-red-500 border-red-500/30" :
                            data?.analytics?.market_status === 'VOLATILE' ? "bg-amber-500/20 text-amber-500 border-amber-500/30" :
                            "bg-[#9d4edd]/20 text-[#9d4edd] border-[#9d4edd]/30"
                        )}>
                            Market_{data?.analytics?.market_status || 'STABLE'}
                        </span>
                    </div>
                    <span className="text-[11px] font-bold uppercase tracking-[0.5em] opacity-30 mb-6 group-hover:text-[#9d4edd] transition-colors">Total_Global_Capital</span>
                    <h2 className="text-9xl font-display font-black text-gradient leading-none tracking-tighter">
                        ₹{Math.floor(totalWealth).toLocaleString()}
                    </h2>
                </div>

                <div className="grid grid-cols-2 gap-8">
                    <div className="nexus-card flex flex-col justify-center p-10">
                        <span className="text-[10px] font-bold uppercase tracking-widest opacity-30 mb-4 text-[#9d4edd]">Active_Nodes</span>
                        <div className="flex items-end gap-3">
                            <span className="text-6xl font-display font-bold">{aliveCount}</span>
                            <span className="text-xl font-bold opacity-20 mb-2">/ 10</span>
                        </div>
                    </div>
                    <div className="nexus-card flex flex-col justify-center p-10">
                        <span className="text-[10px] font-bold uppercase tracking-widest opacity-30 mb-4 text-[#9d4edd]">Inequality_Gini</span>
                        <div className="flex items-end gap-3">
                            <span className="text-6xl font-display font-bold">{gini.toFixed(2)}</span>
                            <span className="text-xl font-bold opacity-20 mb-2">INDX</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                    { label: 'Survival_Food', val: data?.market.food, icon: Heart },
                    { label: 'Kinetic_Energy', val: data?.market.energy, icon: Zap },
                    { label: 'Atomic_Materials', val: data?.market.materials, icon: Database }
                ].map((item, i) => (
                    <div key={i} className="nexus-card p-8 flex items-center justify-between group">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-widest opacity-30 mb-2">{item.label}</span>
                            <span className="text-3xl font-display font-bold">₹{item.val?.toFixed(2) || '0.00'}</span>
                        </div>
                        <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center opacity-40 group-hover:opacity-100 transition-opacity">
                            <item.icon size={20} className="text-[#9d4edd]" />
                        </div>
                    </div>
                ))}
            </div>
        </motion.div>
    );
};

const NexusAnalysis = ({ data }: any) => {
    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 px-12 h-screen overflow-y-auto custom-scrollbar pb-32">
            <div className="flex flex-col mb-12">
                <span className="text-[11px] font-bold uppercase tracking-[0.5em] opacity-30 mb-2">Analysis_System_v3.0</span>
                <h2 className="text-5xl font-display font-bold">Economic Forensics</h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                <div className="lg:col-span-2 nexus-card p-10 flex flex-col h-[400px]">
                    <div className="flex justify-between items-center mb-8">
                        <span className="text-[10px] font-bold uppercase tracking-widest opacity-30 text-[#9d4edd]">Gini_Coefficient_Timeline</span>
                        <div className="px-3 py-1 rounded bg-white/5 border border-white/5 text-[9px] font-black opacity-40 uppercase">Inequality_Trend</div>
                    </div>
                    <div className="flex-1 w-full h-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data?.history || []}>
                                <defs>
                                    <linearGradient id="giniGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#9d4edd" stopOpacity={0.4}/>
                                        <stop offset="95%" stopColor="#9d4edd" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <XAxis dataKey="step" hide />
                                <YAxis domain={[0, 1]} hide />
                                <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #222' }} />
                                <Area type="monotone" dataKey="gini" stroke="#9d4edd" fill="url(#giniGrad)" strokeWidth={3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="nexus-card p-10 flex flex-col h-[400px]">
                    <span className="text-[10px] font-bold uppercase tracking-widest opacity-30 text-[#9d4edd] mb-8 text-center">Wealth_Concentration</span>
                    <div className="flex-1 w-full h-full flex items-end gap-1 px-4">
                        {data?.analytics?.wealth_distribution.map((w: number, i: number) => {
                            const maxW = Math.max(...data?.analytics?.wealth_distribution, 1);
                            const height = (w / maxW) * 100;
                            return (
                                <motion.div 
                                    key={i} 
                                    initial={{ height: 0 }} animate={{ height: `${height}%` }}
                                    className="flex-1 bg-[#9d4edd]/40 rounded-t-sm"
                                    title={`Wealth: ₹${w.toFixed(0)}`}
                                />
                            );
                        })}
                    </div>
                    <div className="mt-6 flex justify-between text-[8px] font-black opacity-20 uppercase tracking-tighter">
                        <span>Poorest_Node</span>
                        <span>Wealthiest_Node</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="nexus-card p-10 h-[300px] flex flex-col">
                    <span className="text-[10px] font-bold uppercase tracking-widest opacity-30 text-[#9d4edd] mb-8">Survival_Velocity</span>
                    <div className="flex-1">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data?.history || []}>
                                <XAxis dataKey="step" hide />
                                <YAxis domain={[0, 1]} hide />
                                <Area type="stepAfter" dataKey="survival_rate" stroke="#00C7B7" fill="#00C7B710" strokeWidth={2} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
                <div className="nexus-card p-10 h-[300px] flex flex-col justify-center text-center">
                    <span className="text-[10px] font-bold uppercase tracking-widest opacity-30 text-[#c77dff] mb-4">Market_Volatility_Index</span>
                    <h3 className="text-7xl font-display font-black">{(data?.analytics?.volatility * 100 || 0).toFixed(1)}%</h3>
                    <div className="mt-4 flex items-center justify-center gap-2">
                         <div className={cn("w-2 h-2 rounded-full", data?.analytics?.volatility > 0.1 ? "bg-amber-500 animate-pulse" : "bg-green-500")} />
                         <span className="text-[9px] font-black opacity-40 uppercase tracking-widest">{data?.analytics?.market_status}</span>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

const FluxStream = ({ data }: any) => (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 px-12 h-screen flex flex-col overflow-hidden pb-32">
        <div className="flex justify-between items-end mb-12">
            <div className="flex flex-col">
                <span className="text-[11px] font-bold uppercase tracking-[0.5em] opacity-30 mb-2">Market_Flux_Gradients</span>
                <h2 className="text-5xl font-display font-bold">Liquid Analytics</h2>
            </div>
            <div className="flex gap-4">
                <div className="bg-[#9d4edd]/10 border border-[#9d4edd]/20 px-6 py-2 rounded-2xl">
                    <span className="text-[10px] font-bold text-[#9d4edd] uppercase tracking-widest">Growth: PROJECTION_NOMINAL</span>
                </div>
            </div>
        </div>

        <div className="flex-1 nexus-card p-0 overflow-hidden relative border-none bg-transparent">
            <div className="flex-1 w-full h-full p-4 relative z-10">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data?.history || []}>
                        <defs>
                            <linearGradient id="fluxPurple" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#9d4edd" stopOpacity={0.6}/>
                                <stop offset="95%" stopColor="#9d4edd" stopOpacity={0}/>
                            </linearGradient>
                            <linearGradient id="fluxDeep" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#5a189a" stopOpacity={0.4}/>
                                <stop offset="95%" stopColor="#5a189a" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="10 10" stroke="#ffffff03" vertical={false} />
                        <XAxis dataKey="step" hide />
                        <YAxis hide domain={['auto', 'auto']} />
                        <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #222', borderRadius: '12px', fontSize: '11px' }} />
                        <Area type="monotone" dataKey="food" stroke="#9d4edd" fill="url(#fluxPurple)" strokeWidth={3} fillOpacity={1} />
                        <Area type="monotone" dataKey="energy" stroke="#c77dff" fill="url(#fluxDeep)" strokeWidth={2} fillOpacity={1} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    </motion.div>
);

const AgentRoster = ({ data }: any) => {
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 px-12 h-screen flex flex-col overflow-y-auto custom-scrollbar pb-32">
            <div className="flex justify-between items-end mb-12">
                <div className="flex flex-col">
                    <h2 className="text-[11px] font-bold uppercase tracking-[1em] opacity-30">Authorized_Agent_Nodes</h2>
                    <span className="text-[10px] font-bold text-[#9d4edd] uppercase tracking-widest mt-2">Mode: MARL_INFERENCE_ACTIVE</span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {data?.agents.map((agent: Agent) => (
                    <motion.div 
                        key={agent.id} 
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedAgent(agent)}
                        className={cn("nexus-card flex items-center justify-between transition-all cursor-pointer group", !agent.alive && "opacity-20 grayscale")}
                    >
                        <div className="flex items-center gap-6">
                            <div className={cn("status-ring", agent.alive && "active")} />
                            <div className="flex flex-col">
                                <div className="flex items-center gap-3 mb-1">
                                    <span className="text-xs font-bold tracking-widest text-[#9d4edd] opacity-60 uppercase">Node_{agent.id.split('_')[1]}</span>
                                    {agent.persona && (
                                        <span className={cn(
                                            "text-[8px] font-black px-2 py-0.5 rounded-full border tracking-widest",
                                            agent.persona === 'RISK_TAKER' ? "bg-red-500/10 text-red-500 border-red-500/20" :
                                            agent.persona === 'CONSERVATIVE' ? "bg-cyan-500/10 text-cyan-500 border-cyan-500/20" :
                                            "bg-amber-500/20 text-amber-500 border-amber-500/30"
                                        )}>
                                            {agent.persona.replace('_', ' ')}
                                        </span>
                                    )}
                                </div>
                                <span className="text-lg font-bold font-display">₹{Math.floor(agent.money).toLocaleString()}</span>
                                {agent.alive && (
                                    <div className="flex flex-col gap-1 mt-2">
                                        <div className="flex items-center gap-2">
                                            <span className="text-[9px] font-black bg-white/5 px-2 py-1 rounded text-white/40 uppercase">{agent.action || 'IDLE'}</span>
                                            <span className={cn("text-[9px] font-black", (agent.reward || 0) >= 0 ? "text-green-400" : "text-red-400")}>
                                                {(agent.reward || 0) > 0 ? "+" : ""}{(agent.reward || 0).toFixed(2)}
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                        <Radio size={16} className="opacity-0 group-hover:opacity-40 transition-opacity text-[#9d4edd]" />
                    </motion.div>
                ))}
            </div>

            <AnimatePresence>
                {selectedAgent && (
                    <motion.div 
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-xl flex items-center justify-center p-12"
                        onClick={() => setSelectedAgent(null)}
                    >
                        <motion.div 
                            initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
                            className="w-full max-w-2xl bg-[#0a0a0a] border border-white/10 rounded-3xl p-12 shadow-2xl relative overflow-hidden"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="absolute top-0 left-0 w-full h-1 bg-[#9d4edd] opacity-50" />
                            <div className="flex justify-between items-start mb-8">
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-black text-[#9d4edd] uppercase tracking-[0.3em] mb-2">Neural_Log_Sequence</span>
                                    <h3 className="text-3xl font-display font-bold">Node_{selectedAgent.id.split('_')[1]} Intelligence</h3>
                                </div>
                                <button onClick={() => setSelectedAgent(null)} className="text-white/20 hover:text-white uppercase text-[10px] font-bold tracking-widest">Close_Log</button>
                            </div>

                            <div className="bg-black/50 border border-white/5 rounded-2xl p-8 max-h-[400px] overflow-y-auto custom-scrollbar font-mono text-sm leading-relaxed">
                                {selectedAgent.logs?.slice().reverse().map((log, idx) => (
                                    <div key={idx} className={cn("mb-8 pb-8 border-b border-white/5 last:border-0 last:mb-0 last:pb-0", idx === 0 ? "text-[#9d4edd]" : "opacity-40")}>
                                        <div className="flex justify-between mb-4">
                                            <span className="text-[10px] font-black uppercase tracking-widest text-[#9d4edd]">Step_{log.step}</span>
                                            <span className="text-[10px] font-black opacity-30 tracking-widest uppercase">Sequence_Captured</span>
                                        </div>
                                        <pre className="whitespace-pre-wrap">
                                            {JSON.stringify(log, null, 2)}
                                        </pre>
                                    </div>
                                ))}
                                {(!selectedAgent.logs || selectedAgent.logs.length === 0) && (
                                    <span className="text-[10px] font-black uppercase tracking-widest opacity-20">No_Logs_Available_In_Memory_Buffer</span>
                                )}
                            </div>

                            <div className="mt-8 grid grid-cols-2 gap-4">
                                <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                    <span className="text-[9px] font-bold opacity-30 uppercase tracking-widest block mb-1">Observation_Stream</span>
                                    <span className="text-xs font-medium opacity-60">Status: Nominal / Markovian</span>
                                </div>
                                <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                    <span className="text-[9px] font-bold opacity-30 uppercase tracking-widest block mb-1">Policy_Certainty</span>
                                    <span className="text-xs font-medium opacity-60">Determinism: [0.85] (Stochastic)</span>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

const KernelOps = ({ resetSim }: any) => {
    const [isGodMode, setIsGodMode] = useState(false);

    const triggerShock = async (type: string) => {
        if (!isGodMode) return;
        await fetch(`/shock/${type}`, { method: 'POST' });
    };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 px-12 h-screen flex flex-col items-center justify-center pb-32">
            <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="nexus-card flex flex-col gap-6 relative overflow-hidden">
                    <div className="flex justify-between items-start">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-[#9d4edd] mb-1">Nexus_Protocol</span>
                            <h3 className="text-2xl font-display font-bold">Safe Mode</h3>
                        </div>
                        <div 
                            className={cn("w-14 h-7 rounded-full p-1 cursor-pointer transition-colors", isGodMode ? "bg-[#9d4edd]" : "bg-white/10")}
                            onClick={() => setIsGodMode(!isGodMode)}
                        >
                            <motion.div 
                                className="w-5 h-5 bg-white rounded-full shadow-lg"
                                animate={{ x: isGodMode ? 28 : 0 }}
                            />
                        </div>
                    </div>
                    <p className="text-xs opacity-40 leading-relaxed">
                        When active, authorized users can perform system-wide interventions. Economic sabotage is disabled by default to prevent cascade failures.
                    </p>
                </div>

                <div className={cn("nexus-card flex flex-col gap-8 transition-all duration-700", !isGodMode && "opacity-20 grayscale pointer-events-none")}>
                    <div className="flex items-center gap-4">
                        <ShieldAlert size={20} className="text-[#9d4edd]" />
                        <h3 className="text-lg font-display font-bold uppercase tracking-widest">Economic Sabotage</h3>
                    </div>
                    <div className="grid grid-cols-1 gap-4">
                        <button onClick={() => triggerShock('food')} className="nexus-card bg-white/5 border border-white/5 py-4 rounded-xl text-[10px] font-black tracking-widest hover:bg-red-500/20 hover:text-red-500 transition-all uppercase text-center">
                            Shock_Survival_Supply
                        </button>
                        <button onClick={() => triggerShock('energy')} className="nexus-card bg-white/5 border border-white/5 py-4 rounded-xl text-[10px] font-black tracking-widest hover:bg-amber-500/20 hover:text-amber-500 transition-all uppercase text-center">
                            Destabilize_Kinetic_Grid
                        </button>
                        <button onClick={() => triggerShock('materials')} className="nexus-card bg-white/5 border border-white/5 py-4 rounded-xl text-[10px] font-black tracking-widest hover:bg-purple-500/20 hover:text-purple-500 transition-all uppercase text-center">
                            Corrupt_Atomic_Materials
                        </button>
                        <button onClick={resetSim} className="nexus-card bg-[#9d4edd]/10 border border-[#9d4edd]/20 py-4 rounded-xl text-[10px] font-black tracking-widest text-[#9d4edd] hover:bg-[#9d4edd] hover:text-black transition-all uppercase text-center mt-4">
                            Perform_Global_Purge
                        </button>
                    </div>
                </div>
            </div>
            
            <div className="mt-16 flex items-center gap-6 opacity-20">
                <div className="h-[1px] w-32 bg-white" />
                <span className="text-[8px] font-black uppercase tracking-[2em]">Kernel_Access_Level_0</span>
                <div className="h-[1px] w-32 bg-white" />
            </div>
        </motion.div>
    );
};

// --- APP ENTRY ---

export default function App() {
  const [data, setData] = useState<SimPayload | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = `ws://${window.location.host}/ws`;
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onmessage = (event) => {
      const payload: SimPayload = JSON.parse(event.data);
      setData(payload);
    };
    return () => ws.current?.close();
  }, []);

  const toggleSim = () => {
    if (!ws.current) return;
    ws.current.send(JSON.stringify({ type: isRunning ? 'STOP' : 'START' }));
    setIsRunning(!isRunning);
  };

  const resetSim = async () => {
    await fetch('/reset', { method: 'POST' });
    setData(null);
    setIsRunning(false);
  };

  return (
    <BrowserRouter>
      <div className="bg-[#050505] text-white selection:bg-[#9d4edd] selection:text-black min-h-screen font-sans overflow-hidden">
          <div className="nexus-aura" />
          
          <NexusHeader step={data?.step} isRunning={isRunning} toggleSim={toggleSim} />
          
          <main className="relative z-10 w-full">
            <AnimatePresence mode="wait">
                <Routes>
                    <Route path="/" element={<NexusOverview data={data} />} />
                    <Route path="/analysis" element={<NexusAnalysis data={data} />} />
                    <Route path="/market" element={<FluxStream data={data} />} />
                    <Route path="/agents" element={<AgentRoster data={data} />} />
                    <Route path="/config" element={<KernelOps resetSim={resetSim} />} />
                </Routes>
            </AnimatePresence>
          </main>

          <NexusNav />
      </div>
    </BrowserRouter>
  );
}
