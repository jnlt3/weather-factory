from dataclasses import dataclass
from subprocess import PIPE, Popen


@dataclass
class MatchResult:
    w: int
    l: int
    d: int
    elo_diff: float


class CutechessMan:

    def __init__(self, engine: str, book: str, games: int = 120, tc: float = 5.0, hash_size: int = 8, threads: int = 1):
        self.engine = engine
        self.book = book
        self.games = games
        self.tc = tc
        self.inc = tc / 100
        self.hash_size = hash_size
        self.threads = threads

    def get_cutechess_cmd(self, params_a: list[str], params_b: list[str]) -> str:
        return f"./tuner/cutechess-cli \
                -engine cmd=./tuner/{self.engine} name={self.engine} proto=uci option.Hash={self.hash_size} {' '.join(params_a)} \
                -engine cmd=./tuner/{self.engine} name={self.engine} proto=uci option.Hash={self.hash_size} {' '.join(params_b)} \
                -resign movecount=3 score=400 \
                -draw movenumber=40 movecount=8 score=10 \
                -recover \
                -concurrency {self.threads} \
                -each tc={self.tc}+{self.inc} \
                -openings file=tuner/{self.book} order=random \
                -games tuner/{self.games} \
                -pgnout games.pgn"

    def run(self, params_a: list[str], params_b: list[str]) -> MatchResult:
        cmd = self.get_cutechess_cmd(params_a, params_b)
        cutechess = Popen(cmd.split(), stdout=PIPE)

        score = [0, 0, 0]
        elo_diff = 0

        while True:

            # Read each line of output until the pipe closes
            line = cutechess.stdout.readline().strip().decode('ascii')
            if line != '':
                print(line)
                # Parse WLD score
                if line.startswith("Score of"):
                    start_index = line.find(":") + 1
                    end_index = line.find("[")
                    split = line[start_index:end_index].split(" - ")

                    for i in range(3):
                        score[i] = int(split[i])

                # Parse Elo Difference
                if line.startswith("Elo difference"):
                    start_index = line.find(":") + 1
                    end_index = line.find("+")
                    elo_diff = float(line[start_index:end_index])
            else:
                cutechess.wait()
                return MatchResult(score[0], score[1], score[2], elo_diff)
