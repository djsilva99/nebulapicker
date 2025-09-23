def identity(to_add: bool):
    return to_add

def title_contains(
    to_add: bool,
    title: str,
    expression: str,
    count: int
):
    if title.lower().count(expression.lower()) < count:
        return False
    return to_add

def description_contains(
    to_add: bool,
    description: str,
    expression: str,
    count: int
):
    if description.lower().count(expression.lower()) < count:
        return False
    return to_add

def title_does_not_contain(
    to_add: bool,
    title: str,
    expression: str,
    count: int
):
    if title.lower().count(expression.lower()) >= count:
        return False
    return to_add

def description_does_not_contain(
    to_add: bool,
    description: str,
    expression: str,
    count: int
):
    if description.lower().count(expression.lower()) >= count:
        return False
    return to_add
