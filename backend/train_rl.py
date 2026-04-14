import os
import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from engine.rl_env import NexusParallelEnv

def train():
    print(">>> INITIALIZING NEURAL KERNEL TRAINING (v9.3 Advanced)...")
    
    # 1. Create the base PettingZoo environment (10 agents, 11x6 space)
    env = NexusParallelEnv(num_agents=10, max_steps=500)
    
    # 2. Wrap it for Stable-Baselines3
    env = ss.black_death_v3(env)
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    env = ss.concat_vec_envs_v1(env, 1, num_cpus=1, base_class="stable_baselines3")
    
    # 3. Define the RL Model (PPO)
    model = PPO(
        MlpPolicy,
        env,
        verbose=1,
        learning_rate=3e-4,
        batch_size=512,
        n_steps=2048,
        gamma=0.99,
        ent_coef=0.02, # Increased for 6-action exploration
        tensorboard_log="./nexus_rl_logs/"
    )
    
    # 4. Train
    print(">>> COMMENCING ADVANCED EVOLUTION (200,000 steps)...")
    model.learn(total_timesteps=200000)
    
    # 5. Save the Nexus Policy
    model_path = os.path.join(os.path.dirname(__file__), "api", "models", "nexus_policy.zip")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f">>> TRAINING COMPLETE. COMPETITIVE POLICY PERSISTED AT: {model_path}")

if __name__ == "__main__":
    train()
