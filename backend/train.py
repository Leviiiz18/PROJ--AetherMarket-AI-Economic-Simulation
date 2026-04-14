import ray
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.policy.policy import PolicySpec
from engine.env import EconomyEnv

def run_training():
    ray.init(ignore_reinit_error=True)

    # Define policy mapping
    # Heterogeneous agents: different policies for different groups
    def policy_mapping_fn(agent_id, episode, worker, **kwargs):
        idx = int(agent_id.split("_")[1])
        if idx < 3:
            return "aggressive_policy"
        elif idx < 7:
            return "efficient_policy"
        else:
            return "stable_policy"

    # Configure the environment
    env_config = {
        "num_agents": 10,
        "max_steps": 500,
    }

    # Setup PPO Configuration
    config = (
        PPOConfig()
        .environment(env=EconomyEnv, env_config=env_config)
        .framework("torch") # Use torch for consistency
        .rollouts(num_rollout_workers=2)
        .multi_agent(
            policies={
                "aggressive_policy": PolicySpec(),
                "efficient_policy": PolicySpec(),
                "stable_policy": PolicySpec(),
            },
            policy_mapping_fn=policy_mapping_fn,
        )
        .training(
            lr=1e-4,
            gamma=0.99,
            lambda_=0.95,
            clip_param=0.2,
            sgd_minibatch_size=64,
            num_sgd_iter=10,
        )
        .resources(num_gpus=0) # Run on CPU for local dev compatibility
    )

    # Run the training
    analysis = tune.run(
        "PPO",
        config=config.to_dict(),
        stop={"training_iteration": 10}, # Short run for demo, increase for real results
        checkpoint_config=tune.CheckpointConfig(
            checkpoint_at_end=True,
            checkpoint_frequency=5,
        ),
        local_dir="./ray_results",
    )

    print("Training completed. Checkpoints saved in ./ray_results")
    return analysis

if __name__ == "__main__":
    run_training()
