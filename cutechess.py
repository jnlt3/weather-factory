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
        tc: str = "5+0.05",
        hash_size: int = 8,
        game_pairs: bool = False,
    ):
        self.engine = engine
        self.book = book
        self.tc = tc
        self.hash_size = hash_size
        self.game_pairs = game_pairs

        self.current_concurrency = 0

    def get_cutechess_cmd(self, params_a: list[str], params_b: list[str]) -> str:
        return (
            "./tuner/cutechess-cli "
            f"-engine cmd=./tuner/{self.engine} name={self.engine} proto=uci "
            f"option.Hash={self.hash_size} {' '.join(params_a)} "
            f"-engine cmd=./tuner/{self.engine} name={self.engine} proto=uci "
            f"option.Hash={self.hash_size} {' '.join(params_b)} "
            "-resign movecount=3 score=400 "
            "-draw movenumber=40 movecount=8 score=10 "
            "-repeat "
            f"-each tc={self.tc} "
            f"-openings file=tuner/{self.book} "
            f"format={self.book.split('.')[-1]} order=random plies=16 "
            f"-games 2 "
            "-pgnout tuner/games.pgn"
        )

    def run(self, params_a: list[str], params_b: list[str]) -> int:
        cmd = self.get_cutechess_cmd(params_a, params_b)
        print(cmd)
        cutechess = Popen(cmd.split(), stdout=PIPE)

        score = [0, 0, 0]

        while True:

            # Read each line of output until the pipe closes
            line = cutechess.stdout.readline().strip().decode("ascii")
            # print(line)
            if not line:
                cutechess.wait()
                if self.game_pairs:
                    if score[0] > score[1]:
                        return 1
                    elif score[0] < score[1]:
                        return -1
                    return 0
                return score[0] - score[1]
            # Parse WLD score
            if line.startswith("Score of"):
                start_index = line.find(":") + 1
                end_index = line.find("[")
                split = line[start_index:end_index].split(" - ")

                score = [int(i) for i in split]
