import argparse

def parse_arguments(name: str, description = None) -> argparse.Namespace:
    if description is None:
        description = f"Runs an instance of a {name} client. "
    parser = argparse.ArgumentParser(prog = name, description=description)
    parser.add_argument("authfile")
    parser.add_argument("-p", "--pool",  dest = "pool", help = "Pool", choices = [0, 1, 2], type = int, default = 2)
    parser.add_argument("-s", "--self-training", dest = "self_training", help = "Self Training", default = False, action = 'store_true')
    parser.add_argument("-r", "--render", dest = "render", help = "Render Gameplay", default = False, action = "store_true")
    parser.add_argument("-n", "--num_games", dest = "num_games", type = int, help = "Number of games", default = 1)
    return parser.parse_args()

