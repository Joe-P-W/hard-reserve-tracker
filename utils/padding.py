
def pad(string: str, max_length: int):
    string_length = len(string)

    if string_length >= max_length:
        return string

    difference = max_length - string_length

    return string + " " * difference