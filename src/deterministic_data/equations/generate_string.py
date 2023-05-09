import concurrent.futures
import functools
import time
from typing import Callable  # Generator, List, Tuple
import random
import re
import numpy as np

# PARAM:
max_length: int = 10
int_size: int = 99


# CONSTS
max_unit_length = (
    ((len(str(int_size)) + 1) * 2) +  # 2 numbers
    3 +  # whitespace op whitespace
    3  # second operator
                  ) * max_length - 3  # last doesnt have 2nd op
operators = ['+', '-', '*', '/']
regex_mult_div = re.compile(r'(-?\d+)\s*([/*]{1,2})\s*(-?\d+)')
regex_sub_add = re.compile(r'(-?\d+)\s*([+-])\s*(-?\d+)')
function_times = {}

def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        global function_times
        start_time = time.perf_counter()  # also time.process_time()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        try:
            function_times[func.__name__] += run_time
        except KeyError:
            function_times[func.__name__] = run_time
        # print(f"Ran {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer

def compute_timing_percentages():
    time_spent = sum(function_times.values())
    return {k: round((v/time_spent)*100, 6) for k, v in function_times.items()}

def coinflip(): return random.choice((True, False))


def random_operator(): return random.choice(operators)

@timer
def generate() -> str:
    """
    Generates a random string of integers up to and including the int_size param paired with random operators from
    the operator's list. The integers will randomly be either positive or negative. Each integer and each operator
    are spaced from each other with a space.

    Example (with int_size of 10): generate() => 1 + -7 // 2 * 10 * -3
    :return:
    """
    result = ''
    iterations = random.randint(1, max_length)
    for cycle in range(iterations):
        second_operator = f' {random_operator()} ' if cycle != iterations - 1 else ''
        neg1 = '-' if coinflip() else ''
        neg2 = '-' if coinflip() else ''
        result += f'{neg1}{random.randint(1, int_size)}' \
                  f' {random_operator()} ' \
                  f'{neg2}{random.randint(1, int_size)}' \
                  f'{second_operator}'
    return result

encoder_map = {
    '0': 0b0000,
    '1': 0b0001,
    '2': 0b0010,
    '3': 0b0011,
    '4': 0b0100,
    '5': 0b0101,
    '6': 0b0110,
    '7': 0b0111,
    '8': 0b1000,
    '9': 0b1001,
    '+': 0b1010,
    '-': 0b1011,
    '/': 0b1100,
    '*': 0b1101,
    ' ': 0b1110,
}
@timer
def encoder(equation_expression: str) -> list[tuple[int, int]]:
    result = [(encoder_map[char], index) for index, char in enumerate(equation_expression)]
    last_index = result[-1][1]
    if last_index < max_unit_length:
        left = max_unit_length - last_index
        for num in range(left):
            result.append((0b1111, last_index + num))
    return result
@timer
def solve(problem: str):
    """
    Solves the generated strings problem with order of operations by iteratively doing each operation in a group until
    there is nothing left and returns the integer of the result.
    EX:
        4 + 4 * 4 // 4 - 4
        A.
            4 + 16 // 4 -4
            4 + 4 - 4
        B.
            8 - 4
            4
    :param problem: String from generate()
    :return: int of solution
    """
    # problem = iteratively_replace(problem, regex_mult_div, calculate_match)
    # problem = iteratively_replace(problem, regex_sub_add, calculate_match)
    # return int(problem)
    if re.search('[a-zA-Z]', problem):
        raise Exception('Words in mathematical eval, danger of hack.')
    return eval(problem.replace('/', '//'))

def calculate_match(match: re.Match) -> str:
    """
    Performs calculation dependent on operator to the numbers found.

    :param match: Must have int operator int their corresponding groups (1,2,3)
    :return: calculate_match((match from '2 * 2')) => '4'
    """
    num1 = int(match.group(1))
    operator = match.group(2)
    num2 = int(match.group(3))
    if operator == '+':
        return str(num1 + num2)
    if operator == '-':
        return str(num1 - num2)
    if operator == '*':
        return str(num1 * num2)
    if operator == '//':
        return str(num1 // num2)

def iteratively_replace(origin: str, pattern: re.Pattern | str, replacement: str | Callable[[re.Match], str]) -> str:
    """
    Iteratively substitutes a pattern to a string. This function is recursive so if the function is caught in an infinite
    loop it will raise a RecursionError. Though if your text has a lot of matches it might be necessary to raise the recursion
    cap. The function checks whether the pattern is found in the replacement and raises an error if that is the case.
    If a string is provided in the pattern param it will use re.compile(pattern) and raise an error on invalid regexs.

    :param origin: The original text to replace.
    :param pattern: Pattern object or text to use in pattern.sub()
    :param replacement: String or func(match) to act as the replacer in pattern.sub()
    :return: String replaced with all replacements in an iterative manner starting from the left of the string to the right.
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    if isinstance(replacement, str):
        if pattern.search(replacement):
            raise re.error('The replacement string contains the substitution so it will infinitely replace itself.')
    match = pattern.search(origin)
    if not match:
        return origin
    new = pattern.sub(replacement, origin, count=1)
    return iteratively_replace(new, pattern, replacement)


def get_a_data(no_problem=False) -> tuple[str, list, int] | tuple[list, int]:
    """
    :return: problem solution pair
    """
    problem = generate()
    if no_problem:
        return encoder(problem), solve(problem)
    return problem, encoder(problem), solve(problem)


def generate_dataset(size: int, no_problem=False, to_np_array=False) -> list[tuple[str, list, int]] | tuple[list[np.ndarray], list[int]]:
    """
    :param to_np_array:
    :param no_problem:
    :param size: Size of dataset
    :return: List of (problem, solution) tuples relative size
    """
    if not to_np_array:
        return [get_a_data(no_problem) for _ in range(size)]
    else:
        result = [get_a_data(True) for _ in range(size)]
        return np.array([i[0] for i in result]), [i[1] for i in result]

def dataset_generator_multiprocess(size: int, divisions: int, no_problem=False, to_np_array=False) -> list[tuple[str, list, int]]:
    """

    :param no_problem: Omits the equation string from the dataset
    :param size: Size of dataset
    :param divisions: MP partitions to calculate with sweet spot is not to many or not too few probably best for a pow 2
    :return:
    """
    with concurrent.futures.ProcessPoolExecutor() as exe:
        futures = [exe.submit(generate_dataset, size//divisions, no_problem=no_problem, to_np_array=to_np_array) for _ in range(divisions)]
        return [thread.result() for thread in futures]

if __name__ == '__main__':
    print(len(generate_dataset(12, to_np_array=True)[0][0]))
    # print(np.array([i[1] for i in generate_dataset(10)]))