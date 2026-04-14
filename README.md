<div align="center">
  <img src="img/L1.png" width="120" alt="AetherMarket Logo" />
  <h1>AetherMarket 🚀 (v12.1)</h1>
  <p><b>Heterogeneous Multi-Agent Reinforcement Learning Arena</b></p>
  
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Reinforcement Learning](https://img.shields.io/badge/Reinforcement--Learning-FFD43B?style=for-the-badge&logo=google-gemini&logoColor=white)](https://en.wikipedia.org/wiki/Reinforcement_learning)
  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Stable Baselines3](https://img.shields.io/badge/SB3-FF6F00?style=for-the-badge&logo=pytorch&logoColor=white)](https://stable-baselines3.readthedocs.io/)
  <br />
  [![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
</div>

---

## 🌟 Overview

**AetherMarket** is a high-fidelity economic laboratory where agents with unique neural identities engage in emergent trade, production, and survival. It transitions from monolithic agent behaviors to a complex, diverse social ecosystem driven by divergent survival strategies.

## 🖼️ Neural Interface Gallery

<div align="center">
  <img src="img/I1.png" width="400" alt="Diagnostic Terminal" />
  <img src="img/I2.png" width="400" alt="Market Flux" />
  <br />
  <img src="img/I3.png" width="400" alt="Neural Chronology" />
  <img src="img/I4.png" width="400" alt="Agent Roster" />
  <br />
  <img src="img/I5.png" width="600" alt="Global Telemetry" />
</div>

## 🏗️ Phase 2 Achievements

- **🎭 Heterogeneous Personas**: Agents are initialized with unique identities—`RISK_TAKERS`, `CONSERVATIVE`, or `OPPORTUNIST`—each driven by specialized reward shaping.
- **📜 Neural Chronology Terminal**: A per-agent diagnostic engine that logs and visualizes the "Reasoning Chain" (`State -> Action -> Reward`) for real-time auditing.
- **👁️ Expanded Sensory Input**: Agents now consume a 14-dimensional information vector including one-hot persona encoding and market trend markers.
- **🧠 Advanced PPO Evolution**: High-fidelity policies trained for 200,000+ steps to handle complex behavioral divergence.

## 📂 Project Structure

```
aether-market/
├── backend/
│   ├── api/            # FastAPI & WebSocket Telemetry
│   ├── engine/         # MARL Environment (RL_Env) & Market Logic
│   └── models/         # Trained Neural Policy Weights (.zip)
├── frontend/           # Vite + React + Tailwind Dashboard
│   ├── src/            # Core UI Logic & Diagnostic Components
│   └── public/img      # Brand Assets & UI Icons
└── shared/             # Standardized schemas and protocols
```

## 🛠️ Setup & Execution

### 1. Backend Orchestration
```bash
cd backend
pip install -r requirements.txt
python api/main.py
```

### 2. Frontend Interface
```bash
cd frontend
npm install
npm run dev
```

## 🎮 How It Works

1. **Environment**: Agents produce, consume, and trade resources in a zero-sum economic loop.
2. **Survival**: Resources are depleted over time. Depletion leads to agent death.
3. **Persona Logic**: A shared policy manages all agents, but the input vector differentiates their roles, causing divergent survival strategies.
4. **Market Clearing**: Prices automatically adjust every step based on the global buy/sell ratio.

---

### 👨‍💻 Author
**Rudranarayan aka Levvizz18**

---
*Built for the study of Emergent Intelligence and Heterogeneous Behavioral Finance.*
