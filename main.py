
import json
from graph import Graph
from spsa import Param, SpsaParams, SpsaTuner
from cutechess import CutechessMan
import copy


def cutechess_from_config(config_path: str) -> CutechessMan:
    with open(config_path) as config_file:
        config = json.load(config_file)
    return CutechessMan(**config)


def params_from_config(config_path: str) -> list[Param]:
    with open(config_path) as config_file:
        config = json.load(config_file)
    return [Param(name, **cfg) for name, cfg in config.items()]


def spsa_from_config(config_path: str):
    with open(config_path) as config_file:
        config = json.load(config_file)
    return SpsaParams(**config)


def main():
    params = params_from_config("config.json")
    cutechess = cutechess_from_config("cutechess.json")
    spsa_params = spsa_from_config("spsa.json")
    spsa = SpsaTuner(spsa_params, params, cutechess)
    graph = Graph()

    while True:
        spsa.step()
        graph.update(copy.deepcopy(spsa.params))
        graph.save("graph.png")
        for param in spsa.params:
            print(param)
        print()


if __name__ == "__main__":
    main()
