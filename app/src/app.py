from components.game import Snake
from components.model import DQN
from components.agent import Agent

def start_game():
    env = Snake()
    model = DQN(11, 256, 3)

    choice = env.main_menu()
    if choice == "quit":
        return
    elif choice == "new":
        agent = Agent(model, force_new=True)
    elif choice == "load":
        agent = Agent(model)
        
    record = agent.record

    try:
        while True:
            state_old = agent.get_state(env)
            action = agent.get_action(state_old)

            reward, done, result = env.step(action, agent.n_games, record)

            if result == 'quit':
                agent.model.save(stats={'record': record, 'n_games': agent.n_games})
                break

            if result == 'menu':
                agent.model.save(stats={'record': record, 'n_games': agent.n_games})
                env.reset()

                choice = env.main_menu()
                if choice == "quit":
                    break
                elif choice == "new":
                    agent = Agent(model, force_new=True)
                elif choice == "load":
                    agent = Agent(model)

                record = agent.record
                env.reset()
                continue

            score = result
            state_new = agent.get_state(env)
            agent.train_short_memory(state_old, action, reward, state_new, done)
            agent.remember(state_old, action, reward, state_new, done)

            if done:
                env.reset()
                agent.n_games += 1
                agent.train_long_memory()

                if isinstance(score, int) and score > record:
                    record = score
                    agent.model.save(stats={'record': record, 'n_games': agent.n_games})

    except KeyboardInterrupt:
        agent.model.save(stats={'record': record, 'n_games': agent.n_games})

if __name__ == '__main__':
    start_game()
