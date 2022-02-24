from spsa import Param
import matplotlib.pyplot as plt


class Graph:
    def __init__(self):
        self.history: list[list[Param]] = []

    def update(self, params: list[Param]):
        self.history.append(params)

    def save(self, file_name: str):
        param_values: dict[str, list[float]] = {}
        for params in self.history:
            for param in params:
                if param.name not in param_values:
                    param_values[param.name] = []
                param_values[param.name].append(
                    (param.value - param.start_val) / param.step)
        for name, value in param_values.items():
            plt.plot(range(len(self.history)), value, label=name)
        plt.legend()
        plt.savefig(f"tuner/{file_name}")
        plt.clf()
