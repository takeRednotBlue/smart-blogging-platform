def list_suggestions(query: str, lis: list) -> list:
    """Returns a list of suggestions from a given list based on a query.

    :param query: The query string to search for in the list.
    :type query: str
    :param lis: The list to search for suggestions.
    :type lis: list
    :return: A list of suggestions that contain the query string (case-insensitive).
    :rtype: list"""
    return [v for v in lis if query.lower() in v.lower()]


def exmple_list_autocoplete(query: str) -> list:
    """Returns a list of autocomplete suggestions of some fruits based on the given query.

    :param query: The query string to search for autocomplete suggestions.
    :type query: str
    :return: A list of autocomplete fruit suggestions.
    :rtype: list"""
    autocomplete_values = ["apple", "banana", "cherry", "date", "fig", "grape"]
    return list_suggestions(query, autocomplete_values)

# def tags_list_autocoplete(session:,query: str) -> list:
#     """Returns a list of autocomplete suggestions of some fruits based on the given query.

#     :param query: The query string to search for autocomplete suggestions.
#     :type query: str
#     :return: A list of autocomplete fruit suggestions.
#     :rtype: list"""
#     autoco
#     # autocomplete_values = ["apple", "banana", "cherry", "date", "fig", "grape"]
#     return list_suggestions(query, autocomplete_values)
