import numpy as np
import random
import functools
from pettingzoo import ParallelEnv
from gymnasium.spaces import Box, Discrete
from .market import GlobalMarket

class NexusParallelEnv(ParallelEnv):
    """
    Advanced MARL Environment for the Neural Oracle.
    Features: Quantized Actions, Social Reward Shaping, and Agent Memory.
    """
    metadata = {"render_modes": ["human"], "name": "nexus_parallel_v2"}

    def __init__(self, num_agents=10, max_steps=500, logger_cb=None):
        super().__init__()
        self.agent_count = num_agents
        self.max_steps = max_steps
        self.logger_cb = logger_cb
        self.agents = [f"agent_{i}" for i in range(num_agents)]
        self.possible_agents = self.agents[:]
        
        # State: [money, food, energy, p_f, p_e, p_m, trend_f, trend_e, trend_m, 
        #         last_action, last_reward, IS_RISK, IS_CONS, IS_OPP]
        self.observation_spaces = {
            agent: Box(low=-1000, high=1e6, shape=(14,), dtype=np.float32)
            for agent in self.agents
        }
        
        # Actions: 0:Hold, 1:Buy_F, 2:Sell_F, 3:Buy_E, 4:Sell_E, 5:Buy_M, 6:Sell_M, 7:Produce, 8:Buy_F_L, 9:Sell_F_L
        self.action_spaces = {
            agent: Discrete(10)
            for agent in self.agents
        }

        self.market = GlobalMarket(volatility=0.15)
        self.render_mode = None
        self.agent_states = {}
        self.prev_prices = {"food": 10.0, "energy": 5.0, "materials": 15.0}
        
        # Memory buffers
        self.last_actions = {agent: 0 for agent in self.agents}
        self.last_rewards = {agent: 0.0 for agent in self.agents}

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent): return self.observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent): return self.action_spaces[agent]

    def reset(self, seed=None, options=None):
        self.market = GlobalMarket()
        self.current_step = 0
        self.agents = self.possible_agents[:]
        self.prev_prices = {"food": 10.0, "energy": 5.0, "materials": 15.0}
        self.last_actions = {agent: 0 for agent in self.agents}
        self.last_rewards = {agent: 0.0 for agent in self.agents}

        self.agent_states = {
            agent: {
                "money": 100.0 + random.uniform(-10, 10),
                "food": 5.0 + random.uniform(-1, 1),
                "energy": 5.0 + random.uniform(-1, 1),
                "materials": 5.0 + random.uniform(-1, 1),
                "alive": True,
                "extinct": False,
                "lives": 3,
                "generation": 1,
                "dynasty_peak": 100.0,
                "cooldown": 0,
                "last_wealth": 100.0,
                "persona": random.choice(["RISK_TAKER", "CONSERVATIVE", "OPPORTUNIST"])
            } for agent in self.agents
        }
        
        # Reset last_wealth to actual randomized total
        for agent, s in self.agent_states.items():
            s["last_wealth"] = s["money"] + (s["food"] * 10.0) + (s["energy"] * 5.0) + (s["materials"] * 15.0)
        
        observations = {agent: self._get_obs(agent) for agent in self.agents}
        return observations, {agent: {} for agent in self.agents}

    def _get_obs(self, agent):
        s = self.agent_states[agent]
        prices = self.market.state.prices
        trends = {
            res: (prices[res] - self.prev_prices[res]) / max(0.1, self.prev_prices[res])
            for res in ["food", "energy", "materials"]
        }
        
        # One-Hot Persona: [Is_Risk, Is_Cons, Is_Opp]
        p = s["persona"]
        persona_vec = [1.0 if p == "RISK_TAKER" else 0.0,
                       1.0 if p == "CONSERVATIVE" else 0.0,
                       1.0 if p == "OPPORTUNIST" else 0.0]

        return np.array([
            s["money"], s["food"], s["energy"],
            prices["food"], prices["energy"], prices["materials"],
            trends["food"], trends["energy"], trends["materials"],
            float(self.last_actions[agent]),
            float(self.last_rewards[agent]),
            *persona_vec
        ], dtype=np.float32)

    def step(self, actions):
        self.current_step += 1
        self.prev_prices = self.market.state.prices.copy()
        
        # 0. Respawn Management (Phase 4)
        for agent, s in self.agent_states.items():
            if not s["alive"]:
                if s["extinct"]:
                    # Extinct agents stay dead for 200 steps, then replaced by "Wild Newcomer"
                    s["cooldown"] -= 1
                    if s["cooldown"] <= -200:
                         print(f">>> [NEWCOMER] {agent} slot reclaimed by fresh neural brain.")
                         self._respawn_agent(agent, is_newcomer=True)
                else:
                    # Heirs respawn after a short 5-step mourning period
                    s["cooldown"] -= 1
                    if s["cooldown"] <= -5:
                        print(f">>> [BIRTH] {agent} Heir G{s['generation']} has entered the arena.")
                        self._respawn_agent(agent, is_newcomer=False)
        
        rewards = {agent: 0.0 for agent in self.agents}
        terminations = {agent: False for agent in self.agents}
        truncations = {agent: False for agent in self.agents}

        # 1. Process Actions
        for agent, action in actions.items():
            s = self.agent_states[agent]
            if not s["alive"]: continue
            
            self.last_actions[agent] = action
            
            if action == 1: self._handle_trade(agent, "food", "buy", 1.0, rewards)
            elif action == 2: self._handle_trade(agent, "food", "sell", 1.0, rewards)
            elif action == 3: self._handle_trade(agent, "energy", "buy", 1.0, rewards)
            elif action == 4: self._handle_trade(agent, "energy", "sell", 1.0, rewards)
            elif action == 5: self._handle_trade(agent, "materials", "buy", 1.0, rewards)
            elif action == 6: self._handle_trade(agent, "materials", "sell", 1.0, rewards)
            elif action == 7: # Produce
                if s["energy"] >= 1 and s["materials"] >= 1:
                    s["energy"] -= 1; s["materials"] -= 1; s["food"] += 2
                    rewards[agent] += 1.0
                else: rewards[agent] -= 0.5
            elif action == 8: self._handle_trade(agent, "food", "buy", 5.0, rewards)
            elif action == 9: self._handle_trade(agent, "food", "sell", 5.0, rewards)

        # 2. Environment Dynamics
        self.market.step()
        
        # 3. Competition Analytics
        total_wealth = 0
        alive_agents = 0
        agent_wealths = {}
        prices = self.market.state.prices
        
        for agent in self.agents:
            s = self.agent_states[agent]
            if s["alive"]:
                # Current Wealth = Cash + Inventory (valued at CURRENT market price for Phase 3)
                inv_val = (s["food"] * prices["food"]) + (s["energy"] * prices["energy"]) + (s["materials"] * prices["materials"])
                w = s["money"] + inv_val
                agent_wealths[agent] = w
                total_wealth += w
                alive_agents += 1
        
        avg_wealth = total_wealth / max(1, alive_agents)

        # 4. Final Reward Shaping
        prices = self.market.state.prices
        trends = {
            res: (prices[res] - self.prev_prices[res]) / max(0.1, self.prev_prices[res])
            for res in ["food", "energy", "materials"]
        }

        for agent in self.agents:
            s = self.agent_states[agent]
            if s["alive"]:
                # Basic Needs
                s["food"] -= 0.15 # Reduced for Phase 4 survival
                if s["food"] <= 0:
                    self._handle_agent_death(agent, "Starvation", rewards, terminations)
                else:
                    rewards[agent] += 1.0 # Significant survival bonus
                    
                    # Wealth Multiplier
                    w = agent_wealths[agent]
                    wealth_delta = w - s["last_wealth"]
                    rewards[agent] += wealth_delta * 0.2

                    # --- PERSONA SPECIALIZATION ---
                    persona = s["persona"]
                    if persona == "RISK_TAKER":
                        if s["food"] > 15: rewards[agent] += 0.5 # Hoarding bonus
                        if action in [2, 4]: rewards[agent] += 0.3 # Aggressive trade bonus
                    elif persona == "CONSERVATIVE":
                        if wealth_delta > 0 and wealth_delta < 5: rewards[agent] += 0.5 # Stability bonus
                        if s["food"] > 10: rewards[agent] -= 0.3 # Stockpile risk penalty
                    elif persona == "OPPORTUNIST":
                        if action in [1, 2] and trends["food"] < -0.1: rewards[agent] += 0.8
                        if action in [3, 4] and trends["food"] > 0.1: rewards[agent] += 0.8

                    s["last_wealth"] = w
                    
                    # COMPETITION PRESSURE
                    rewards[agent] += (w - avg_wealth) * 0.05
                    
                    # Bankruptcy Fear
                    if s["money"] < 20: rewards[agent] -= (2.0 / (s["money"] + 1))
            
            self.last_rewards[agent] = rewards[agent]

        if self.current_step >= self.max_steps:
            truncations = {agent: True for agent in self.agents}

        observations = {agent: self._get_obs(agent) for agent in self.agents}
        return observations, rewards, terminations, truncations, {agent: {} for agent in self.agents}

    def get_analytics(self):
        """Phase 3 Analytical Export"""
        alive_wealths = [
            s["money"] + (s["food"] * self.market.state.prices["food"]) + 
            (s["energy"] * self.market.state.prices["energy"]) + 
            (s["materials"] * self.market.state.prices["materials"])
            for s in self.agent_states.values() if s["alive"]
        ]
        
        # 1. Gini Coefficient
        gini = 0.0
        if len(alive_wealths) > 1:
            array = np.array(alive_wealths)
            index = np.arange(1, len(array) + 1)
            n = len(array)
            gini = ((np.sum((2 * index - n  - 1) * np.sort(array))) / (n * np.sum(array)))
        
        # 2. Market Metrics
        m_metrics = self.market.get_market_metrics("food")
        
        # 3. Survival
        total = self.agent_count
        alive = len(alive_wealths)
        
        return {
            "gini": float(gini),
            "volatility": m_metrics["volatility"],
            "market_status": m_metrics["status"],
            "contagion_index": float(self.market.state.contagion_index),
            "survival_rate": float(alive / total),
            "wealth_distribution": [float(w) for w in sorted(alive_wealths)]
        }

    def _handle_agent_death(self, agent, reason, rewards, terminations):
        s = self.agent_states[agent]
        s["alive"] = False
        terminations[agent] = True
        rewards[agent] -= 100.0  # Heavy penalty for dying
        
        # DYNASTY AUDIT (Phase 4)
        current_peak = s["last_wealth"]
        improved = current_peak > s["dynasty_peak"]
        
        s["lives"] -= 1
        msg = f"DYNASTY ALERT: {agent} died ({reason}). G{s['generation']}, Peak: ₹{s['dynasty_peak']:.1f}, Lives left: {s['lives']}"
        print(f">>> {msg}")
        if self.logger_cb: self.logger_cb(msg)
        
        if improved:
            s["dynasty_peak"] = current_peak
        
        if s["lives"] <= 0:
            if not improved:
                s["extinct"] = True
                emsg = f"[EXTINCTION] {agent} culling triggered. Failed to improve wealth."
                print(f">>> {emsg}")
                if self.logger_cb: self.logger_cb(emsg)
            else:
                # Earned a reset (rebirth)
                s["extinct"] = False
                s["lives"] = 3
                s["generation"] += 1
                bmsg = f"[EVOLUTION] {agent} setting new dynasty peak. G{s['generation']} incoming."
                print(f">>> {bmsg}")
                if self.logger_cb: self.logger_cb(bmsg)
        else:
            # Heir spawning protocol (standard respawn)
            s["generation"] += 1
            hmsg = f"[HEIR] {agent} G{s['generation']} reporting for duty."
            print(f">>> {hmsg}")
            if self.logger_cb: self.logger_cb(hmsg)

    def _handle_trade(self, agent, resource, order_type, qty, rewards):
        s = self.agent_states[agent]
        price = self.market.get_price(resource)
        total_cost = price * qty
        
        if order_type == "buy":
            if s["money"] >= total_cost:
                s["money"] -= total_cost
                s[resource] += qty
                self.market.submit_order(agent, resource, qty, "buy")
            else: rewards[agent] -= 0.5
        else: # Sell
            if s[resource] >= qty:
                s[resource] -= qty
                s["money"] += total_cost
                self.market.submit_order(agent, resource, qty, "sell")
                rewards[agent] += 0.2
            else: rewards[agent] -= 0.2

    def _respawn_agent(self, agent, is_newcomer=False):
        s = self.agent_states[agent]
        s["alive"] = True
        s["money"] = 100.0 + random.uniform(-10, 10)
        s["food"] = 10.0 + random.uniform(-1, 1) # Support Phase 4 buff
        s["energy"] = 5.0 + random.uniform(-1, 1)
        s["materials"] = 5.0 + random.uniform(-1, 1)
        s["last_wealth"] = 100.0
        s["cooldown"] = 0
        
        if is_newcomer:
            s["extinct"] = False
            s["lives"] = 3
            s["generation"] = 1
            s["dynasty_peak"] = 100.0
            s["persona"] = random.choice(["RISK_TAKER", "CONSERVATIVE", "OPPORTUNIST"])
