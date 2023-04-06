def sort_dictionary(unsorted_dict: dict[str, ], reverse=False):
    """A util function to sort the keys of a dictionary.

    Parameters
    ---------
    - unsorted_dict`dict[str, Any]`: The dictionary that needs to be sorted.
    - reverse`bool`: Whether the keys need to be sorted in reverse order.

    Returns
    ------
    - sorted_dict`dict[str, Any]`: The dictionary with keys sorted.
    """
    order_list: list[str] = sorted(unsorted_dict.keys(), reverse=reverse)
    sorted_dictionary = {i: unsorted_dict[i] for i in order_list}
    return sorted_dictionary