from flask import Flask, request
from model_files.snake_model import TestSnake
from playgroundrl.client import Pool
app = Flask(__name__)


snake_model = None

@app.route('/')
def home():
    return '<h1>Hello from Flask & Docker</h2>'

@app.route('/load')
def load():
    global snake_model
    snake_model = TestSnake(
        "auth.txt", 
        False,
    )
    print(snake_model)
    return '<h1>Loaded Successfully</h2>'

@app.route('/save')
def save():
    return '<h1>Saved Model</h2>'

@app.route('/start_game')
def start_game():
    global snake_model
    print(snake_model)
    if snake_model is None:
        return '<h1>Model not started</h2>'
    else:
        pool = Pool(int(request.args.get('pool')))
        num_games = int(request.args.get('num_games'))
        snake_model.run(
            pool=pool,
            num_games=num_games,
            self_training=False,
            maximum_messages=500000
        )
        return '<h1>Started Model</h2>'

@app.route('/health_check')
def health_check():
    global snake_model
    if snake_model is None:
        return '<h1>Unhealthy</h2>'
    else:
        return '<h1>Healthy</h2>'


if __name__ == "__main__":
    app.run(debug=True)
