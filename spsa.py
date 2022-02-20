

from dataclasses import dataclass
import random
import copy


class Param:
    def __init__(self, name: str, value: int, min_value: int, max_value: int, elo_per_val: float):
        assert elo_per_val > 0
        self.name = name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.elo_per_val = elo_per_val

    def get(self) -> int:
        return int(self.value)

    def update(self, amt: float):
        self.value += amt
        self.value = min(max(self.value, self.min_value), self.max_value)

    def to_uci(self) -> str:
        return f"option.{self.name}={self.get()}"

    def pretty(self) -> str:
        return f"{self.name} = {self.get()} in [{self.min_value}, {self.max_value}] with Elo diff {self.elo_per_val}"


@dataclass
class SpsaParams:
    a: float
    c: float
    A: int
    alpha: float = 0.6
    gamma: float = 0.1
    target_elo: float = 10


class SpsaTuner:

    def __init__(self, spsa_params: SpsaParams, uci_params: list[Param]):
        self.spsa = spsa_params
        self.uci_params = uci_params
        self.delta = [0] * len(uci_params)
        self.t = 0

    def step(self):
        a_t = self.spsa.a / (self.t + 1 + self.spsa.A) ** self.spsa.alpha
        c_t = self.spsa.c / (self.t + 1) ** self.spsa.gamma
        self.t += 1

        for i in range(len(self.delta)):
            self.delta[i] = random.randint(0, 1) * 2 - 1

        uci_params_a = []
        uci_params_b = []
        for (param, delta) in zip(self.uci_params, self.delta):
            curr_delta = self.spsa.target_elo / param.elo_per_val

            step = delta * curr_delta * c_t

            uci_a = copy.deepcopy(param)
            uci_b = copy.deepcopy(param)

            uci_a.update(step)
            uci_b.update(-step)

            uci_params_a.append(uci_a)
            uci_params_b.append(uci_b)

        gradient = self.gradient(uci_params_a, uci_params_b)

        for (param, delta) in zip(self.uci_params, self.delta):
            param_grad = gradient / (delta * c_t)
            param.update(-param_grad * a_t)

    def params(self) -> list[Param]:
        return self.uci_params

    def gradient(self, params_a: list[Param], params_b: list[Param]) -> float:
        # TODO: play games with cute chess
        return 0.0
