
import json
from graph import Graph
from spsa import Param, SpsaParams, SpsaTuner
from cutechess import CutechessMan
import copy


def cutechess_from_config(config: str) -> CutechessMan:
    with open(config, "r") as config:
        config = json.load(config)
        return CutechessMan(config["engine"],
                            config["book"],
                            config["games"],
                            config["tc"],
                            config["hash"],
                            config["threads"])


def params_from_config(config: str):
    with open(config, "r") as config:
        params = []
        config = json.load(config)
        for name in config:
            param = config[name]
            params.append(Param(
                name,
                param["value"],
                param["min_value"],
                param["max_value"],
                param["elo_per_val"]
            ))
        return params


def spsa_from_config(config: str):
    with open(config, "r") as config:
        config = json.load(config)
        return SpsaParams(config["a"], config["c"], config["A"], config["alpha"], config["gamma"], config["elo"])


def main():
    params = params_from_config("config.json")
    cutechess = cutechess_from_config("cutechess.json")
    spsa_params = spsa_from_config("spsa.json")
    spsa = SpsaTuner(spsa_params, params, cutechess)
    graph = Graph()

    while True:
        spsa.step()
        graph.update(copy.deepcopy(spsa.params()))
        graph.save("graph.png")
        for param in spsa.params():
            print(param.pretty())


if __name__ == "__main__":
    main()
