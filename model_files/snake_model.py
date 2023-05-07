from playgroundrl.client import *
from .util import parse_arguments
import time 

# The following line are an example of how to use the API
class TestSnake(PlaygroundClient):
    def __init__(
        self, 
        auth_file: str,
        render: bool = False
    ):
        super().__init__(
            GameType.SNAKE,
            model_name="stock-snake",
            auth_file=auth_file,
            render_gameplay=render,
        )

    def callback(self, state: SnakeState, reward):
        # Assume string is (apple_x, apple_y); [(snake_x, snake_y), ...]
        # Assume board size is even
        # Apply a basic strategy that will keep snake alive as long as
        # possible and eventually cover the whole board, ignoring the apple
        # apple, snake = self._parse_state(state)
        apple = state.apple
        snake = state.snake 
        head = snake[-1]

        SIZE = 10
        x, y = head

        time.sleep(0.05)
        if x == SIZE -1 and y == SIZE - 2:
            return "S"

        if x == 0 and y == SIZE - 1:
            return "N"

        if y == SIZE - 1:
            return "W"

        if x % 2 == 0:
            if y == 0:
                return "E"
            return "N"
        else:
            if y == SIZE - 2:
                return "E"
            return "S"

    def gameover_callback(self):
        pass


