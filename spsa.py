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
    step: float

    def __post_init__(self):
        self.start_val: float = self.value
        assert self.step > 0

    def get(self) -> int:
        return round(self.value)

    def update(self, amt: float):
        self.value = min(max(self.value + amt, self.min_value), self.max_value)

    @property
    def as_uci(self) -> str:
        return f"option.{self.name}={self.get()}"

    def get_change(self) -> str:
        if self.value > self.start_val:
            return f"+{self.value - self.start_val:.2f}"
        elif self.value < self.start_val:
            return f"-{self.start_val - self.value:2f}"
        else:
            return f"+-0"

    def __str__(self) -> str:
        return (
            f"{self.name} = {self.get()}({self.get_change()}) in "
            f"[{self.min_value}, {self.max_value}] "
        )


@dataclass
class SpsaParams:
    a: float
    c: float
    A: int
    alpha: float = 0.601
    gamma: float = 0.102


@dataclass
class SpsaTest:
    params_a: list[Param]
    params_b: list[Param]
    delta: list[int]
    t: int


class SpsaTuner:
    def __init__(
        self, spsa_params: SpsaParams, uci_params: list[Param], cutechess: CutechessMan
    ):
        self.uci_params = uci_params
        self.spsa = spsa_params
        self.cutechess = cutechess
        self.t = 0

    def get_tests(self):
        self.t += 1
        c_t = self.spsa.c / self.t**self.spsa.gamma

        delta_list = [randint(0, 1) * 2 - 1 for _ in range(len(self.uci_params))]

        uci_params_a = []
        uci_params_b = []
        for param, delta in zip(self.uci_params, delta_list):
            curr_delta = param.step

            step = delta * curr_delta * c_t

            uci_a = copy.deepcopy(param)
            uci_b = copy.deepcopy(param)

            uci_a.update(step)
            uci_b.update(-step)

            uci_params_a.append(uci_a)
            uci_params_b.append(uci_b)

        return SpsaTest(uci_params_a, uci_params_b, delta_list, self.t)

    def step(self, test: SpsaTest):
        gradient = self.gradient(test.params_a, test.params_b)
        a_t = self.spsa.a / (test.t + self.spsa.A) ** self.spsa.alpha
        c_t = self.spsa.c / test.t**self.spsa.gamma

        for param, delta in zip(self.uci_params, test.delta):
            param_grad = gradient / (delta * c_t)
            param.update(-param_grad * a_t * param.step)

    @property
    def params(self) -> list[Param]:
        return self.uci_params

    def gradient(self, params_a: list[Param], params_b: list[Param]) -> float:
        str_params_a = [p.as_uci for p in params_a]
        str_params_b = [p.as_uci for p in params_b]
        game_result = self.cutechess.run(str_params_a, str_params_b)
        return game_result.l - game_result.w
