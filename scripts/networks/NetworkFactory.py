from cares_reinforcement_learning.algorithm.policy import TD3, SAC, DDPG
import torch

def create_SAC(observation_size, action_num, alg_config):
    from networks.SAC import Actor
    from networks.SAC import Critic

    actor  = Actor(observation_size, action_num, alg_config.actor_lr)
    critic = Critic(observation_size, action_num, alg_config.critic_lr)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    agent = SAC(
        actor_network=actor,
        critic_network=critic,
        gamma=alg_config.gamma,
        tau=alg_config.tau,
        actor_lr=alg_config.actor_lr,
        critic_lr=alg_config.critic_lr,
        action_num=action_num,
        device=device,
    )
    
    return agent

def create_DDPG(observation_size, action_num, alg_config):
    from networks.DDPG import Actor
    from networks.DDPG import Critic

    actor  = Actor(observation_size, action_num, alg_config.actor_lr)
    critic = Critic(observation_size, action_num, alg_config.critic_lr)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    agent = DDPG(
        actor_network=actor,
        critic_network=critic,
        gamma=alg_config.gamma,
        tau=alg_config.tau,
        actor_lr=alg_config.actor_lr,
        critic_lr=alg_config.critic_lr,
        action_num=action_num,
        device=device,
    )
    
    return agent

def create_TD3(observation_size, action_num, alg_config):
    from networks.TD3 import Actor
    from networks.TD3 import Critic

    actor  = Actor(observation_size, action_num)
    critic = Critic(observation_size, action_num)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    agent = TD3(
        actor_network=actor,
        critic_network=critic,
        gamma=alg_config.gamma,
        tau=alg_config.tau,
        actor_lr=alg_config.actor_lr,
        critic_lr=alg_config.critic_lr,
        action_num=action_num,
        device=device,
    )
    
    return agent

class NetworkFactory:
    def create_network(self, observation_size, action_num, alg_config):
        algorithm = alg_config.algorithm
        if algorithm == "TD3":
            return create_TD3(observation_size, action_num, alg_config)
        elif algorithm == "DDPG":
            return create_DDPG(observation_size, action_num, alg_config)
        elif algorithm == "SAC":
            return create_SAC(observation_size, action_num, alg_config)
        
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
        