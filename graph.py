from spsa import Param
import matplotlib.pyplot as plt


class Graph:
    def __init__(self):
        self.time: list[int] = []
        self.history: list[list[Param]] = []

    def update(self, time: list[int], params: list[Param]):
        self.time.append(time)
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
            plt.plot(self.time, value, label=name)
        plt.legend(fontsize=6, loc="upper left")
        plt.savefig(f"tuner/{file_name}", dpi=250)
        plt.clf()
        
