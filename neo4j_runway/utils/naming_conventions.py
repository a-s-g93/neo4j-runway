import regex as re


def fix_node_label(label: str) -> str:
    """
    Apply Neo4j naming convention PascalCase to a node label.
    """

    if is_mixed_case(label):
        parts = re.findall("[A-Z_ ][^A-Z_ ]*", label[0].upper() + label[1:])
        return "".join([x.capitalize().strip() for x in parts if x != "_"])

    elif is_pascal_case(label):
        return remove_spaces(label)

    elif is_camel_case(label):
        return label[0].upper() + remove_spaces(label[1:])

    elif is_snake_case(label):
        parts = remove_spaces(label).split("_")
        return "".join([x.capitalize() for x in parts])

    else:
        return "".join([x.capitalize().strip() for x in label.split(" ")])


def fix_relationship_type(type: str) -> str:
    """
    Apply Neo4j naming convention SCREAMING_SNAKE_CASE to a relationship type.
    """

    if is_mixed_case(type):
        if "_" not in type:
            return type.upper()
        parts = re.findall("[A-Z_][^A-Z_]*", type[0].upper() + type[1:])
        return "_".join([x.upper() for x in parts if x != "_"])

    elif is_snake_case(type):
        return type.upper()

    elif is_pascal_case(type):
        parts = re.findall("[A-Z][^A-Z]*", type)
        return "_".join(x.upper() for x in parts)

    elif is_camel_case(type):
        parts = re.findall("[A-Z][^A-Z]*", type[0].upper() + type[1:])
        return "_".join(x.upper() for x in parts)
    else:
        return type.upper().replace(" ", "_")


def fix_property(property_name: str) -> str:
    """
    Apply Neo4j naming convention camelCase to a property name.
    """
    # treat property with spaces as snakecase property
    property_name = property_name.replace(" ", "_")
    if is_mixed_case(property_name):
        parts = re.findall(
            "[A-Z_][^A-Z_]*", property_name[0].upper() + property_name[1:]
        )
        pascal = "".join([x.lower().capitalize() for x in parts if x != "_"])
        return pascal[0].lower() + pascal[1:]

    elif is_camel_case(property_name):
        return property_name

    elif is_pascal_case(property_name):
        return property_name[0].lower() + property_name[1:]

    elif is_snake_case(property_name):
        parts = property_name.split("_")
        pascal = "".join([x.capitalize() for x in parts])
        return pascal[0].lower() + pascal[1:]
    else:
        return property_name


def is_camel_case(input: str) -> bool:
    """
    Determine if input is camel case.
    """

    assert len(input) > 0, "No input provided!"

    # first letter capital
    if ord(input[0]) >= 65 and ord(input[0]) <= 90:
        return False

    return not "_" in input and not " " in input


def is_pascal_case(input: str) -> bool:
    """
    Determine if input is Pascal case.
    """

    assert len(input) > 0, "No input provided!"

    # first letter not capital
    if ord(input[0]) < 65 or ord(input[0]) > 90:
        return False

    return not "_" in input and not " " in input


def is_snake_case(input: str) -> bool:
    """
    Determine if input is snake case.
    """

    assert len(input) > 0, "No input provided!"

    return ("_" in input or input.isupper()) and not " " in input


def is_mixed_case(input: str) -> bool:
    """
    Determine if input is mix of camel, pascal or snake case.
    """

    assert len(input) > 0, "No input provided!"

    camel_or_pascal = False
    snake = False

    for i in range(len(input)):
        if (
            input[i].isupper()
            and i > 0
            and input[i - 1].islower()
            and i < len(input) - 1
            and input[i + 1].islower()
        ):
            camel_or_pascal = True
            break

    if "_" in input or input.isupper():
        snake = True

    return camel_or_pascal and snake


def remove_spaces(text: str) -> str:
    """
    Remove the spaces from a text string.
    """
    return text.replace(" ", "")
