from flask import Flask, request, Response
from model_files.snake_model import TestSnake
from model_files.codenames_vec import TestCodenames
from playgroundrl.client import Pool


app = Flask(__name__)


model = None
running = False


@app.route("/")
def home():
    return "<h1>Hello from Flask & Docker</h2>"


@app.route("/load")
def load():
    print("LOADING")
    global model
    if model is None:
        # TODO: Abstract this
        model = TestCodenames(
            "auth.txt",
            False,
        )
        # print(model)
    return "<h1>Loaded Successfully</h2>"


@app.route("/save")
def save():
    return "<h1>Saved Model</h2>"


@app.route("/start_game")
def start_game():
    print("START GAME")
    global model
    global running
    # print(model)
    if model is None:
        print("MODEL NOT STARTED")
        return "<h1>Model not started</h2>"
    else:
        pool = Pool(int(request.args.get("pool")))
        num_games = int(request.args.get("num_games"))
        # Potentially make this nonblocking
        running = True
        model.run(
            pool=pool,
            num_games=num_games,
            self_training=False,
            maximum_messages=500000,
            wait_for_game_end=False,
            # TODO: DO THIS BETTER
            game_parameters={"num_players": 4},
        )
        print("AFTER RETURN")

        # Hack to return to the client early
        response = Response("<h1>Started Model</h2>")

        @response.call_on_close
        def on_close():
            print("WAITING FOR CLOSE")
            model.wait_for_game()
            global running
            running = False
            print("FINISHED ON CLOSE ")

        return response


@app.route("/health_check")
def health_check():
    # See if container is live
    global model
    return Response("OK", status=200)


@app.route("/available")
def available():
    # See if container is live and can run model
    global model

    print("RUNNING", running)
    if model is not None and not running:
        return Response("Available", status=200)

    return Response("Busy", status=400)


if __name__ == "__main__":
    app.run(debug=True)
