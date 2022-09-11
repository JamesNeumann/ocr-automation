def translate(value, from_min, from_max, to_min, to_max):
    """
    Translate the given value from the given range to new range
    :param value: Value to translate
    :param from_min: Minimum value of the value range
    :param from_max: Maximum value of the value range
    :param to_min: Minimum of the new value range
    :param to_max: Maximum of the new value range
    :return: The translated value
    """
    left_span = from_max - from_min
    right_span = to_max - to_min

    value_scaled = float(value - from_min) / float(left_span)

    return to_min + (value_scaled * right_span)
