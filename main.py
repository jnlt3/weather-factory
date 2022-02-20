
from spsa import Param, SpsaParams, SpsaTuner


def main():
    params = [Param("test", 50, 0, 100, 0.5)]
    spsa = SpsaTuner(SpsaParams(0.1, 1.0, 100), params)
    for i in range(100):
        spsa.step()
        for param in spsa.params():
            print(param.pretty())


if __name__ == "__main__":
    main()
