from helper import score


def solve(values):
    return max(values, key=score)
