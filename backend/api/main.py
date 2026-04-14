import sys
import os
import asyncio
from collections import deque
import json
import random
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from stable_baselines3 import PPO

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.rl_env import NexusParallelEnv

app = FastAPI()

# --- SIMULATION STATE ---
NUM_AGENTS = 10
env = NexusParallelEnv(num_agents=NUM_AGENTS)
active_connections: List[WebSocket] = []
running = False

# --- RL POLICY LOADING ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "nexus_policy.zip")
rl_model = None

def load_policy():
    global rl_model
    if os.path.exists(MODEL_PATH):
        print(f">>> RL KERNEL: LOADING COMPETITIVE POLICY FROM {MODEL_PATH}")
        rl_model = PPO.load(MODEL_PATH)
    else:
        print(">>> RL KERNEL: NO ELITE POLICY FOUND. STANDBY.")

load_policy()

# --- API ROUTES ---

@app.post("/reset")
async def reset_sim():
    global env
    env = NexusParallelEnv(num_agents=NUM_AGENTS)
    load_policy()
    print(">>> KERNEL RESET: STATE PURGED")
    return {"status": "reset"}

@app.post("/shock/{resource}")
async def apply_shock(resource: str):
    env.market.apply_shock(resource, 2.0)
    print(f">>> KERNEL SHOCK: {resource} INJECTED")
    return {"status": "shocked", "resource": resource}

# --- SIMULATION LOOP ---

async def run_simulation():
    global running, env
    step = 0
    history = []
    agent_logs = {aid: deque(maxlen=20) for aid in env.agents}
    
    # Reset env to start
    obs, _ = env.reset()
    
    print("\n>>> NEURAL ORACLE: ADVANCED RL IGNITION SEQUENCE STARTING...")
    
    while running:
        # 1. Decision Phase (Advanced MARL)
        actions = {}
        active_aids = []

        for aid in env.agents:
            if env.agent_states[aid]["alive"]:
                current_obs = env._get_obs(aid)
                if rl_model:
                    action, _ = rl_model.predict(current_obs, deterministic=False)
                    actions[aid] = int(action)
                else:
                    actions[aid] = 0 # Hold
                active_aids.append(aid)

        # 2. Environment Step
        new_obs, rewards, terminations, truncations, infos = env.step(actions)
        market_prices = env.market.state.prices
        
        # 3. History Payload
        history_entry = {
            "step": step,
            "food": market_prices["food"],
            "energy": market_prices["energy"],
            "materials": market_prices["materials"]
        }
        history.append(history_entry)
        if len(history) > 60: history.pop(0)

        # Generate Logs
        for aid in env.agents:
            state = env.agent_states[aid]
            log_entry = {
                "agent": aid.split('_')[1],
                "step": step,
                "state": [round(state["money"],2), round(state["food"],2), round(market_prices["food"],2)],
                "action": ["HOLD", "BUY_S", "BUY_L", "SELL_S", "SELL_L", "PROD"][actions.get(aid, 0)],
                "reward": round(rewards.get(aid, 0), 2),
                "reason": "policy_output"
            }
            agent_logs[aid].append(log_entry)

        # Build Neural Payload (Grounded RL Telemetry)
        payload = {
            "step": step,
            "market": market_prices,
            "agents": [
                {
                    "id": aid,
                    "money": state["money"],
                    "food": state["food"],
                    "alive": state["alive"],
                    "reward": round(rewards.get(aid, 0), 2),
                    "action": ["HOLD", "BUY_S", "BUY_L", "SELL_S", "SELL_L", "PROD"][actions.get(aid, 0)],
                    "persona": state["persona"],
                    "logs": list(agent_logs[aid])
                }
                for aid, state in env.agent_states.items()
            ],
            "history": history
        }
        
        # 5. Broadcast
        if active_connections:
            msg = json.dumps(payload)
            dead = []
            for ws in active_connections:
                try:
                    await ws.send_text(msg)
                except:
                    dead.append(ws)
            for d in dead:
                if d in active_connections: active_connections.remove(d)
        
        if step % 10 == 0:
            avg_reward = sum(rewards.values()) / max(1, len(active_aids))
            print(f"--- RL ADVANCED | Step {step} | Alive: {len(active_aids)} | Avg Social Reward: {avg_reward:.2f} ---")
            
        step += 1
        await asyncio.sleep(0.3) # Slightly faster loop
        
        if not active_aids:
            running = False
            print(">>> NEURAL ORACLE: ALL ENTITIES EXTERMINATED.")
            break

# --- WEBSOCKET ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global running
    await websocket.accept()
    active_connections.append(websocket)
    print(f">>> WEBSOCKET UPLINK SECURED: {websocket.client.host}")
    try:
        while True:
            data = await websocket.receive_text()
            cmd = json.loads(data)
            if cmd.get("type") == "START":
                if not running:
                    running = True
                    asyncio.create_task(run_simulation())
            elif cmd.get("type") == "STOP":
                running = False
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)

# --- STATIC FILES ---

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def get_index():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path): return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
