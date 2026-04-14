import numpy as np
import gymnasium as gym
from gymnasium.spaces import Box, Dict, Discrete
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from .market import GlobalMarket

class EconomyEnv(MultiAgentEnv):
    """
    A multi-agent environment simulating a resource-based economy.
    Agents must manage their inventories, trade in the global market, and survive.
    """
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.num_agents = self.config.get("num_agents", 10)
        self.max_steps = self.config.get("max_steps", 500)
        
        # Initialize market
        self.market = GlobalMarket()
        
        # Define the agent IDs
        self._agent_ids = [f"agent_{i}" for i in range(self.num_agents)]
        
        # Spaces
        # Observation: [Money, Food, Energy, Materials, Price_F, Price_E, Price_M]
        self.observation_space = Box(
            low=0, high=1e6, shape=(7,), dtype=np.float32
        )
        
        # Action space: 11 Discrete actions
        self.action_space = Discrete(11) 
        
        self.action_map = {
            0: "Idle",
            1: "Buy Food",
            2: "Sell Food",
            3: "Buy Energy",
            4: "Sell Energy",
            5: "Buy Materials",
            6: "Sell Materials",
            7: "Produce (E+M->F)",
            8: "Consume (Eat)",
            9: "Generate Energy",
            10: "Mine Materials"
        }

        self.reset()

    def reset(self, *, seed=None, options=None):
        self.market = GlobalMarket()
        self.current_step = 0
        
        # Initialize agent states
        self.agents_state = {
            aid: {
                "money": 100.0,
                "food": 10.0,
                "energy": 5.0,
                "materials": 5.0,
                "alive": True
            } for aid in self._agent_ids
        }
        
        obs = self._get_obs()
        return obs, {}

    def _get_obs(self):
        prices = [
            self.market.get_price("food"),
            self.market.get_price("energy"),
            self.market.get_price("materials")
        ]
        
        obs = {}
        for aid in self._agent_ids:
            s = self.agents_state[aid]
            if s["alive"]:
                obs[aid] = np.array([
                    s["money"], s["food"], s["energy"], s["materials"],
                    *prices
                ], dtype=np.float32)
        return obs

    def step(self, action_dict):
        self.current_step += 1
        rewards = {aid: 0.0 for aid in action_dict.keys()}
        terminateds = {"__all__": False}
        truncateds = {"__all__": False}
        
        # Process actions
        for aid, action in action_dict.items():
            state = self.agents_state[aid]
            if not state["alive"]: continue
            
            # Action logic
            if action == 1: # Buy Food
                self._handle_trade(aid, "food", "buy", rewards)
            elif action == 2: # Sell Food
                self._handle_trade(aid, "food", "sell", rewards)
            elif action == 3: # Buy Energy
                self._handle_trade(aid, "energy", "buy", rewards)
            elif action == 4: # Sell Energy
                self._handle_trade(aid, "energy", "sell", rewards)
            elif action == 5: # Buy Materials
                self._handle_trade(aid, "materials", "buy", rewards)
            elif action == 6: # Sell Materials
                self._handle_trade(aid, "materials", "sell", rewards)
            elif action == 7: # Produce (Uses 1 Energy + 1 Material -> 3 Food)
                if state["energy"] >= 1 and state["materials"] >= 1:
                    state["energy"] -= 1
                    state["materials"] -= 1
                    state["food"] += 3
                    rewards[aid] += 0.5 # Production incentive
            elif action == 8: # Consume (Survival)
                if state["food"] >= 1:
                    state["food"] -= 1
                    rewards[aid] += 2.0 # High value for survival
                else:
                    rewards[aid] -= 1.0 # Hunger penalty
            elif action == 9: # Generate Energy
                state["energy"] += 2
                rewards[aid] += 0.2
            elif action == 10: # Mine Materials
                state["materials"] += 2
                rewards[aid] += 0.2
                    
        # Update Market
        self.market.step()
        
        # Hunger check at end of step
        for aid in self._agent_ids:
            state = self.agents_state[aid]
            if state["alive"]:
                # Auto-consume (metabolism)
                state["food"] -= 0.1 
                if state["food"] <= 0:
                    state["alive"] = False
                    rewards[aid] -= 20.0 # Heavy death penalty
                
                # Small wealth reward to keep them interested in growth
                rewards[aid] += state["money"] / 1000.0
            
        # Check termination
        if self.current_step >= self.max_steps:
            terminateds["__all__"] = True
            
        obs = self._get_obs()
        infos = {aid: {} for aid in self._agent_ids}
        
        # Dead agents are terminated individually
        for aid in self._agent_ids:
            if not self.agents_state[aid]["alive"]:
                terminateds[aid] = True

        return obs, rewards, terminateds, truncateds, infos

    def _handle_trade(self, aid, resource, order_type, rewards):
        state = self.agents_state[aid]
        price = self.market.get_price(resource)
        qty = 1.0
        
        if order_type == "buy":
            cost = price * qty
            if state["money"] >= cost:
                state["money"] -= cost
                state["food" if resource == "food" else ("energy" if resource == "energy" else "materials")] += qty
                self.market.submit_order(aid, resource, qty, "buy")
                rewards[aid] += 0.1 # Trade incentive
            else:
                rewards[aid] -= 0.5 # Failed trade penalty
        else: # Sell
            res_key = "food" if resource == "food" else ("energy" if resource == "energy" else "materials")
            if state[res_key] >= qty:
                state[res_key] -= qty
                state["money"] += price * qty
                self.market.submit_order(aid, resource, qty, "sell")
                rewards[aid] += 0.1
            else:
                rewards[aid] -= 0.5
