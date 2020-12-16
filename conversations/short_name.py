"""Generating short label for operator address."""


def unique_label(operator):
    """Function for generating short name for operator from it's address. It takes first 6 and last 4 symbols and
    combines it. """
    return operator[:6] + operator[-4:]
