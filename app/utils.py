from typing import Iterable


def group_by(property_function: callable, collection: Iterable) -> dict:
    result = dict()
    for item in collection:
        item_property = property_function(item)
        if item_property not in result:
            result[item_property] = []
        result[item_property].append(item)
    return result
