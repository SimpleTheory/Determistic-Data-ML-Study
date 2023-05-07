from deterministic_data.equations.generate_string import *

def speed_checks():
    # @timer
    def x():
        return [i for i in generate_dataset(100_000)]


    print(x())
    print(function_times)
    print(compute_timing_percentages())

    @timer
    def x_thread():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(generate_dataset, 100_000) for _ in range(10)]
            return [thread.result() for thread in futures]


    # x_thread()
    @timer
    def x_multiprocess():
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
        #         print('%d is prime: %s' % (number, prime))
        with concurrent.futures.ProcessPoolExecutor() as exe:
            futures = [exe.submit(generate_dataset, 100_000) for _ in range(10)]
            return [thread.result() for thread in futures]
        # with concurrent.futures.ProcessPoolExecutor as exe:
        #     for result in exe.map(get_a_data):


    # x_multiprocess()