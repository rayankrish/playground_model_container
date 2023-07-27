from playgroundrl.client import *
from .util import parse_arguments
import numpy as np
from scipy import spatial
from sklearn.cluster import KMeans
import random

BOARD_SIZE = 25


# The following line are an example of how to use the API
class TestCodenames(PlaygroundClient):
    def __init__(self, auth_file: str, render: bool = False):
        super().__init__(
            GameType.CODENAMES,
            model_name="embedded-codenames-docker",
            auth_file=auth_file,
            render_gameplay=render,
        )
        self.embeddings_dict = {}
        with open("./model_files/glove.6B.300d.txt", "r", encoding="utf-8") as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], "float32")
                self.embeddings_dict[word] = vector
        print("finished loading embeddings dictionary!")
        self.board_vectors = []
        self.words_set = set([])
        self.clues_given = set(
            []
        )  # use this to ensure we don't give the same clue twice
        self.current_clue = ["", 0]  # keep track of whether we are done guessing

    def find_closest_embeddings(self, embedding):
        return sorted(
            self.embeddings_dict.keys(),
            key=lambda word: -spatial.distance.euclidean(
                self.embeddings_dict[word], embedding
            ),
        )

    def get_open_square(self, state: CodenamesState):
        for i in range(BOARD_SIZE):
            if state.guessed[i] == "UNKNOWN":
                return i

    def rank_board_by_sim(self, word):
        all_positions = list(range(BOARD_SIZE))
        word_vec = self.embeddings_dict[word]
        order = sorted(
            all_positions,
            key=lambda pos: spatial.distance.euclidean(
                self.board_vectors[pos], word_vec
            ),
        )
        print("ORDER", order)
        return order

    def callback(self, state: CodenamesState, reward):
        if state.player_moving_id not in self.player_ids:
            return None
        if len(self.board_vectors) == 0:
            for word in state.words:
                if word not in self.embeddings_dict:
                    self.embeddings_dict[word] = self.embeddings_dict[
                        "clue"
                    ]  # TODO: improve this
            self.board_vectors = [self.embeddings_dict[word] for word in state.words]
        print(self.board_vectors)
        if len(self.words_set) == 0:
            self.words_set = set(state.words)

        action = None
        if state.role == "GIVER":
            words_remaining = []
            for i in range(BOARD_SIZE):
                if state.guessed[i] == "UNKNOWN" and state.actual[i] == state.color:
                    words_remaining.append(state.words[i])

            # always give a clue for one word which is randomly picked
            desired_word = words_remaining[random.randrange(len(words_remaining))]
            ordered_words = self.find_closest_embeddings(
                self.embeddings_dict[desired_word]
            )
            ordered_words = ordered_words[1:]
            for word in ordered_words:
                print(word, desired_word)
                if (
                    word not in self.words_set
                    and word not in self.clues_given
                    # Check if word is a substring of our goal word
                    and desired_word not in word
                ):
                    self.clues_given.add(word)
                    action = {"word": word, "count": 1}
                    break

        elif state.role == "GUESSER":
            # if clue is not in the dict, give first available
            if state.clue not in self.embeddings_dict:
                print("DEFAULTING")
                action = {"guess": self.get_open_square(state)}
                return json.dumps(action)

            # if count for this clue is done, end turn
            if not self.current_clue[0] == state.clue:
                self.current_clue = [state.clue, state.count]
            elif self.current_clue[1] == 0:
                action = {"guess": -1}
                return json.dumps(action)
            else:
                self.current_clue[1] -= 1

            # find the unknown word on the board that is closest to the clue
            order = self.rank_board_by_sim(state.clue)
            for i in order:
                print(state.words[i])
                if state.guessed[i] == "UNKNOWN":
                    action = {"guess": i}
                    break
        return json.dumps(action)

    def gameover_callback(self):
        pass


if __name__ == "__main__":
    args = parse_arguments("codenames")
    t = TestCodenames(args.authfile, args.render)
    t.run(
        pool=Pool(args.pool),
        num_games=args.num_games,
        self_training=args.self_training,
        maximum_messages=500000,
        game_parameters={"num_players": 4},
    )
