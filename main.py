
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


def main():
    params = params_from_config("config.json")
    cutechess = cutechess_from_config("cutechess.json")
    spsa = SpsaTuner(SpsaParams(0.1, 1.0, 100), params, cutechess)
    graph = Graph()

    while True:
        spsa.step()
        graph.update(copy.deepcopy(spsa.params()))
        graph.save("graph.png")
        for param in spsa.params():
            print(param.pretty())


if __name__ == "__main__":
    main()
