import argparse
import dataclasses
import json
from math import radians
import pathlib
import sys
import time
from graph import Graph
from spsa import Param, SpsaParams, SpsaTuner
from cutechess import CutechessMan
import copy
import threading


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


def save_state(spsa: SpsaTuner):
    save_file = "./tuner/state.json"
    spsa_params = spsa.spsa
    uci_params = spsa.uci_params
    t = spsa.t
    with open(save_file, "w") as save_file:
        spsa_params = dataclasses.asdict(spsa_params)
        uci_params = [dataclasses.asdict(uci_param) for uci_param in uci_params]

        json.dump(
            {"t": t, "spsa_params": spsa_params, "uci_params": uci_params}, save_file
        )


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=str, default="config.json", help="Config JSON file"
    )
    parser.add_argument(
        "--spsa", type=str, default="spsa.json", help="SPSA parameters JSON file"
    )
    parser.add_argument(
        "--cutechess", type=str, default="cutechess.json", help="cutechess-cli options"
    )
    parser.add_argument(
        "--threads", type=int, default=1, help="Maximum amount of threads to use"
    )
    args = parser.parse_args()

    state_path = pathlib.Path("./tuner/state.json")
    t = 0
    if state_path.is_file():
        print("hey")
        with open(state_path) as state:
            state_dict = json.load(state)
            params = [
                Param(
                    cfg["name"],
                    cfg["value"],
                    cfg["min_value"],
                    cfg["max_value"],
                    cfg["step"],
                )
                for cfg in state_dict["uci_params"]
            ]
            spsa_params = SpsaParams(**state_dict["spsa_params"])
            t = state_dict["t"]
    else:
        params = params_from_config(args.config)
        spsa_params = spsa_from_config(args.spsa)
    cutechess = cutechess_from_config(args.cutechess)
    spsa = SpsaTuner(spsa_params, params, cutechess)
    spsa.t = t
    graph = Graph()

    global AVG_TIME
    AVG_TIME = 0

    start_t = t

    global LOCK
    global TEST_COUNT
    global MAX_TEST_COUNT
    LOCK = threading.Lock()
    TEST_COUNT = 0
    MAX_TEST_COUNT = args.threads

    start = time.time()

    try:
        while True:

            def do_test():
                global AVG_TIME
                global LOCK
                global TEST_COUNT
                global MAX_TEST_COUNT

                test = spsa.get_tests()
                LOCK.acquire()
                TEST_COUNT += 1
                LOCK.release()
                spsa.step(test)
                LOCK.acquire()
                TEST_COUNT -= 1
                LOCK.release()

            LOCK.acquire()
            if TEST_COUNT < MAX_TEST_COUNT:
                LOCK.release()
                threading.Thread(target=do_test).start()

                graph.update(spsa.t, copy.deepcopy(spsa.params))
                graph.save("graph.png")
                print(
                    f"iterations: {spsa.t} ({((time.time() - start) / (spsa.t - start_t)):.2f}s per iter)"
                )
                for param in spsa.params:
                    print(param)
                print()
            else:
                LOCK.release()
    finally:
        print("Saving state...")
        save_state(spsa)


if __name__ == "__main__":
    main()
