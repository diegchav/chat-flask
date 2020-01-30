def is_float(num):
    """
    Check if a given number is of float type.

    :param num: Number to check
    :return: True if num is of type float, False otherwise
    """
    if isinstance(num, str):
        try:
            f = float(num)
            return True
        except ValueError:
            return False
    else:
        return isinstance(num, float)