from cutechess import CutechessMan
from dataclasses import dataclass
from random import randint
import copy


@dataclass
class Param:
    name: str
    value: float
    min_value: int
    max_value: int
    elo_per_val: float

    def __post_init__(self):
        assert self.elo_per_val > 0

    def get(self) -> int:
        return round(self.value)

    def update(self, amt: float):
        self.value = min(max(self.value + amt, self.min_value), self.max_value)

    @property
    def as_uci(self) -> str:
        return f"option.{self.name}={self.get()}"

    def __str__(self) -> str:
        return (
            f"{self.name} = {self.get()} in "
            f"[{self.min_value}, {self.max_value}] "
            f"with Elo diff {self.elo_per_val}"
        )


@dataclass
class SpsaParams:
    a: float
    c: float
    A: int
    alpha: float = 0.6
    gamma: float = 0.1
    target_elo: float = 2


class SpsaTuner:

    def __init__(
        self,
        spsa_params: SpsaParams,
        uci_params: list[Param],
        cutechess: CutechessMan
    ):
        self.uci_params = uci_params
        self.spsa = spsa_params
        self.cutechess = cutechess
        self.delta = [0] * len(uci_params)
        self.t = 0

    def step(self):
        self.t += 1
        a_t = self.spsa.a / (self.t + self.spsa.A) ** self.spsa.alpha
        c_t = self.spsa.c / self.t ** self.spsa.gamma

        self.delta = [randint(0, 1) * 2 - 1 for _ in range(len(self.delta))]

        uci_params_a = []
        uci_params_b = []
        for param, delta in zip(self.uci_params, self.delta):
            curr_delta = self.spsa.target_elo / param.elo_per_val

            step = delta * curr_delta * c_t

            uci_a = copy.deepcopy(param)
            uci_b = copy.deepcopy(param)

            uci_a.update(step)
            uci_b.update(-step)

            uci_params_a.append(uci_a)
            uci_params_b.append(uci_b)

        gradient = self.gradient(uci_params_a, uci_params_b)

        for param, delta, param in zip(self.uci_params, self.delta, self.uci_params):
            param_grad = gradient / (delta * c_t * param.elo_per_val)
            param.update(-param_grad * a_t)

    @property
    def params(self) -> list[Param]:
        return self.uci_params

    def gradient(self, params_a: list[Param], params_b: list[Param]) -> float:
        str_params_a = [p.as_uci for p in params_a]
        str_params_b = [p.as_uci for p in params_b]
        game_result = self.cutechess.run(str_params_a, str_params_b)
        return -game_result.elo_diff
