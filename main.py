
import json
import time
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

    avg_time = 0

    try:
        while True:
            start = time.time()
            spsa.step()
            avg_time += time.time() - start

            graph.update(spsa.t, copy.deepcopy(spsa.params))
            graph.save("graph.png")
            print(f"iterations: {spsa.t} ({(avg_time / spsa.t):.2f}s per iter)")
            for param in spsa.params:
                print(param)
            print()
    finally:
        print("Saving state...")


if __name__ == "__main__":
    main()
