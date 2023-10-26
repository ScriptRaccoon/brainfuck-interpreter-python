"""
Brainfuck interpreter written in Python
https://en.wikipedia.org/wiki/Brainfuck

Usage:
python brainfuck.py [file path]
or
python brainfuck.py [file path] debug
"""


import sys

ALLOWED_CHARS = list("+-><[].,")


def generate_bracket_dict(program: str) -> dict[int, int]:
    """
    Generates a dictionary of bracket infos for a brainfuck program.
    When a bracket [ starts at position i and ends with ] at position j,
    the dictionary has i: j as well as j: i.

    Arguments:
        program: any valid Brainfuck program

    Returns:
        The bracket dictionary

    Raises:
        SyntaxError: When the brackets do not match up
    """
    bracket_dict: dict[int, int] = {}
    opening_bracket_positions = []
    for pos, char in enumerate(program):
        if char == "[":
            opening_bracket_positions.append(pos)
        elif char == "]":
            if len(opening_bracket_positions) == 0:
                raise SyntaxError(f"] in position {pos} has no matching [")
            opening_bracket = opening_bracket_positions.pop()
            bracket_dict[opening_bracket] = pos
            bracket_dict[pos] = opening_bracket
    if len(opening_bracket_positions) > 0:
        pos = opening_bracket_positions[0]
        raise SyntaxError(f"[ in position {pos} has no matching ]")
    return bracket_dict


def interpret(program: str, debug=False) -> None:
    """
    Python interpreter of a brainfuck program.
    It keeps track of
        - a pointer to the current position of the program
        - the index of the current cell
        - the tape, encoded as a list of integers

    Arguments:
        program: any valid Brainfuck program as a string
        debug (optional): if True, prints the current state at each step

    Raises:
        IndexError: when the tape index is negative
    """
    if debug:
        print("program:", program)

    pointer: int = 0
    cell: int = 0
    tape: list[int] = [0]

    bracket_dict = generate_bracket_dict(program)

    while pointer < len(program):
        char: str = program[pointer]

        if not char in ALLOWED_CHARS:
            pointer += 1
            continue

        if debug:
            tape_with_pos = ", ".join(
                str(val) if i != cell else f"|{str(val)}|" for i, val in enumerate(tape)
            )
            print("tape:", tape_with_pos)
            print("char:", char)

        if char == "+":
            tape[cell] += 1
            if tape[cell] > 255:
                tape[cell] = 0

        elif char == "-":
            tape[cell] -= 1
            if tape[cell] < 0:
                tape[cell] = 255

        elif char == ">":
            cell += 1
            if cell >= len(tape):
                tape.append(0)

        elif char == "<":
            if cell == 0:
                raise IndexError("Tape does not have negative indices")
            cell -= 1

        elif char == "[":
            if tape[cell] == 0:
                if debug:
                    print("skip loop")
                pointer = bracket_dict[pointer]
            elif debug:
                print("enter loop")

        elif char == "]":
            if tape[cell] != 0:
                if debug:
                    print("restart loop")
                pointer = bracket_dict[pointer]
            elif debug:
                print("finish loop")

        elif char == ".":
            ascii_value = tape[cell]
            string_value = chr(ascii_value)
            if debug:
                print("print:", string_value)
            else:
                print(string_value, end="")

        elif char == ",":
            string_value = ""
            valid = False
            while not valid:
                string_value = input()
                valid = len(string_value) == 1 and 0 <= ord(string_value) <= 255
                if not valid:
                    print(
                        "Error: Expected only one ascii character as input. Try again."
                    )
            ascii_value = ord(string_value)
            tape[cell] = ascii_value

        pointer += 1


def main() -> None:
    """
    Executes the interpreter with a file passed as an argument
    """
    args = sys.argv
    if len(args) == 1:
        raise ValueError("Missing file path")
    file_path = sys.argv[1]
    debug = len(args) == 3 and args[2] == "debug"
    with open(file_path, "r", encoding="utf8") as file:
        program = file.read()
        interpret(program, debug)


if __name__ == "__main__":
    main()
