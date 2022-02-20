import copy
from spsa import Param
from matplotlib import pyplot as plt


class Graph:
    def __init__(self):
        self.history = []

    def update(self, params: list[Param]):
        self.history.append(params)

    def save(self, file_name: str):
        iters = list(range(len(self.history)))
        param_values = {}
        for params in self.history:
            for param in params:
                if param.name not in param_values:
                    param_values[param.name] = []
                param_values[param.name].append(param.value)
        for param in param_values:
            plt.plot(iters, param_values[param], label=param)
        plt.savefig(f"tuner/{file_name}")
