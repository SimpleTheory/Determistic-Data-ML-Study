from deterministic_data.equations.generate_string import *


def speed_checks():
    @timer
    def x():
        return [i for i in generate_dataset(1_000_000)]

    @timer
    def x_thread():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(generate_dataset, 1_000_000//8, no_problem=False, to_np_array=False) for _ in range(8)]
            return [thread.result() for thread in futures]

    # x_thread()
    @timer
    def x_multiprocess():
        with concurrent.futures.ProcessPoolExecutor() as exe:
            futures = [exe.submit(generate_dataset, 100_000, no_problem=False, to_np_array=False) for _ in range(00)]
            return [thread.result() for thread in futures]

    return [x_multiprocess]
    # x_multiprocess()


if __name__ == '__main__':
    funcs = speed_checks()
    for func in funcs:
        func()
        print(func.__name__)
        print(function_times[func.__name__])

