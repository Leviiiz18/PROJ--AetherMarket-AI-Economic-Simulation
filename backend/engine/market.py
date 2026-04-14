import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

@dataclass
class MarketState:
    prices: Dict[str, float] = field(default_factory=lambda: {
        "food": 10.0,
        "energy": 5.0,
        "materials": 15.0
    })
    total_supply: Dict[str, float] = field(default_factory=lambda: {k: 1000.0 for k in ["food", "energy", "materials"]})
    total_demand: Dict[str, float] = field(default_factory=lambda: {k: 0.0 for k in ["food", "energy", "materials"]})
    history: List[Dict[str, float]] = field(default_factory=list)
    volatility_history: Dict[str, List[float]] = field(default_factory=lambda: {k: [] for k in ["food", "energy", "materials"]})

class GlobalMarket:
    """
    Centralized clearing house for the economy.
    Uses a simple supply-demand ratio to adjust prices dynamically.
    """
    def __init__(self, volatility: float = 0.05, inflation_rate: float = 0.001):
        self.state = MarketState()
        self.volatility = volatility
        self.inflation_rate = inflation_rate
        self.orders: List[Dict] = []

    def submit_order(self, agent_id: str, resource: str, quantity: float, order_type: str):
        """
        Record an order for the current step.
        order_type: 'buy' or 'sell'
        """
        self.orders.append({
            "agent_id": agent_id,
            "resource": resource,
            "quantity": abs(quantity),
            "type": order_type
        })

    def step(self):
        """
        Clears orders and updates prices based on supply/demand.
        """
        # Calculate net supply/demand for the step
        step_demand = {k: 0.0 for k in self.state.prices.keys()}
        step_supply = {k: 0.0 for k in self.state.prices.keys()}

        for order in self.orders:
            res = order["resource"]
            if res in step_demand:
                if order["type"] == "buy":
                    step_demand[res] += order["quantity"]
                else:
                    step_supply[res] += order["quantity"]

        # Update prices
        for res in self.state.prices:
            # Price discovery formula: 
            # P_next = P_curr * (1 + inflation + (demand - supply) / max(1, supply+demand) * volatility)
            d = step_demand[res]
            s = step_supply[res]
            
            # Basic ratio adjustment
            if d + s > 0:
                imbalance = (d - s) / max(1.0, d + s)
                shift = (self.inflation_rate + imbalance * self.volatility)
                self.state.prices[res] *= (1 + shift)
            else:
                # Slight inflation if no trades
                self.state.prices[res] *= (1 + self.inflation_rate)
            
            # Ensure prices stay positive
            self.state.prices[res] = max(0.1, self.state.prices[res])
            
            # Reset totals for next step stats
            self.state.total_demand[res] = d
            self.state.total_supply[res] = s
            
            # --- VOLATILITY & CRASH DETECTION (Phase 3) ---
            v_hist = self.state.volatility_history[res]
            v_hist.append(self.state.prices[res])
            if len(v_hist) > 20: v_hist.pop(0)

        # Record history
        snapshot = {
            "step": len(self.state.history),
            **{f"price_{k}": v for k, v in self.state.prices.items()},
            **{f"demand_{k}": v for k, v in self.state.total_demand.items()},
            **{f"supply_{k}": v for k, v in self.state.total_supply.items()}
        }
        self.state.history.append(snapshot)
        
        # Clear orders for next step
        self.orders = []

    def get_price(self, resource: str) -> float:
        return self.state.prices.get(resource, 0.0)

    def get_market_metrics(self, resource: str = "food"):
        """Calculates Volatility and Crash status for a specific resource"""
        v_hist = self.state.volatility_history.get(resource, [])
        if len(v_hist) < 5:
            return {"volatility": 0.0, "status": "STABLE"}
        
        # Volatility = Standard Deviation of last 10 steps
        recent = v_hist[-10:]
        vol = float(np.std(recent) / max(0.1, np.mean(recent)))
        
        # Crash Detection = Current price 15% lower than 5-step average
        avg_5 = np.mean(v_hist[-5:])
        curr = self.state.prices[resource]
        
        status = "STABLE"
        if curr < avg_5 * 0.85:
            status = "CRASH"
        elif vol > 0.1:
            status = "VOLATILE"
            
        return {"volatility": vol, "status": status}

    def apply_shock(self, resource: str, multiplier: float):
        """Random market shock multiplier"""
        if resource in self.state.prices:
            self.state.prices[resource] *= multiplier
