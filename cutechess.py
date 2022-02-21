from dataclasses import dataclass
from subprocess import PIPE, Popen


@dataclass
class MatchResult:
    w: int
    l: int
    d: int
    elo_diff: float


class CutechessMan:

    def __init__(
        self,
        engine: str,
        book: str,
        games: int = 120,
        tc: float = 5.0,
        hash: int = 8,
        threads: int = 1
    ):
        self.engine = engine
        self.book = book
        self.games = games
        self.tc = tc
        self.inc = tc / 100
        self.hash_size = hash
        self.threads = threads

    def get_cutechess_cmd(
        self,
        params_a: list[str],
        params_b: list[str]
    ) -> str:
        return (
            "./tuner/cutechess-cli "
            f"-engine cmd=./tuner/{self.engine} name={self.engine} proto=uci "
            f"option.Hash={self.hash_size} {' '.join(params_a)} "
            f"-engine cmd=./tuner/{self.engine} name={self.engine} proto=uci "
            f"option.Hash={self.hash_size} {' '.join(params_b)} "
            "-resign movecount=3 score=400 "
            "-draw movenumber=40 movecount=8 score=10 "
            "-repeat "
            "-recover "
            f"-concurrency {self.threads} "
            f"-each tc={self.tc}+{self.inc} "
            f"-openings file=tuner/{self.book} "
            f"format={self.book.split('.')[-1]} order=random plies=16 "
            f"-games {self.games} "
            "-pgnout tuner/games.pgn"
        )

    def run(self, params_a: list[str], params_b: list[str]) -> MatchResult:
        cmd = self.get_cutechess_cmd(params_a, params_b)
        cutechess = Popen(cmd.split(), stdout=PIPE)

        score = [0, 0, 0]
        elo_diff = 0.0

        while True:

            # Read each line of output until the pipe closes
            line = cutechess.stdout.readline().strip().decode('ascii')
            if line:
                print(line)
            else:
                cutechess.wait()
                return MatchResult(*score, elo_diff)
            # Parse WLD score
            if line.startswith("Score of"):
                start_index = line.find(":") + 1
                end_index = line.find("[")
                split = line[start_index:end_index].split(" - ")

                score = [int(i) for i in split]

            # Parse Elo Difference
            if line.startswith("Elo difference"):
                start_index = line.find(":") + 1
                end_index = line.find("+")
                elo_diff = float(line[start_index:end_index])
