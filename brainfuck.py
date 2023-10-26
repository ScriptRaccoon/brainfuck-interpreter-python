"""
Brainfuck interpreter written in Python
https://en.wikipedia.org/wiki/Brainfuck

Usage:
python brainfuck.py example1.bf
or
python brainfuck.py example1.bf debug
"""

from collections.abc import Callable
import sys


class BrainfuckInterpreter:
    """
    Creates a Brainfuck interpreter for a given Brainfuck program

    Arguments:
        program: any Brainfuck program (as a string)
        debug (optional): if True, the interpreter displays the commands and the tape in each step

    Attributes:
        program: the Brainfuck program
        debug: the flag determining if the interpreter prints debug info
        bracket_dict: a dictionary containing matching bracket positions
        pos: current position of the program during interpretation
        tape: the array of integers on which the program operates
        cell: the index of the current cell on the tape
        actions: a dictionary mapping each Brainfuck character to an action
    """

    ALLOWED_CHARS = list("+-><[].,")
    """List of allowed characters in a Brainfuck program, all others are just ignored."""

    def __init__(self, program: str, debug: bool = False) -> None:
        """
        Initializes the Brainfuck interpreter

        Arguments:
            program: any Brainfuck program (as a string)
            debug (optional): if True, interpreter displays commands and tape in each step
        """
        self.program = program
        self.debug = debug
        self.pos: int = 0
        self.tape: list[int] = [0]
        self.cell: int = 0
        self.bracket_dict: dict[int, int] = self.generate_bracket_dict()
        self.actions: dict[str, Callable[[], None]] = self.generate_action_dict()

    def increment(self) -> None:
        """Increments the current cell value (restricted to 1 byte)"""
        self.tape[self.cell] += 1
        if self.tape[self.cell] > 255:
            self.tape[self.cell] = 0

    def decrement(self) -> None:
        """Decrements the current cell value (restricted to 1 byte)"""
        self.tape[self.cell] -= 1
        if self.tape[self.cell] < 0:
            self.tape[self.cell] = 255

    def go_right(self) -> None:
        """Go right on the tape"""
        self.cell += 1
        if self.cell >= len(self.tape):
            self.tape.append(0)

    def go_left(self) -> None:
        """Go left on the tape (if possible)"""
        if self.cell == 0:
            raise IndexError("Tape does not have negative indices")
        self.cell -= 1

    def start_loop(self) -> None:
        """Start the loop: either skip it (when the call value is 0) or enter it"""
        if self.tape[self.cell] == 0:
            if self.debug:
                print("skip loop")
            self.pos = self.bracket_dict[self.pos]
        elif self.debug:
            print("enter loop")

    def finish_loop(self) -> None:
        """Finish the loop: either finish it (when the cell value is 0) or restart it over"""
        if self.tape[self.cell] != 0:
            if self.debug:
                print("restart loop")
            self.pos = self.bracket_dict[self.pos]
        elif self.debug:
            print("finish loop")

    def print(self) -> None:
        """Prints the current cell value as an ascii character"""
        ascii_index = self.tape[self.cell]
        ascii_char = chr(ascii_index)
        if self.debug:
            print("print:", ascii_char)
        else:
            print(ascii_char, end="")

    def read(self) -> None:
        """
        Reads one ascii character from the standard input
        and puts its ascii index on the current cell
        """
        ascii_char = ""
        valid = False
        while not valid:
            ascii_char = input()
            valid = len(ascii_char) == 1 and 0 <= ord(ascii_char) <= 255
            if not valid:
                print("Error: Expected only one ascii character as input. Try again.")
        ascii_index = ord(ascii_char)
        self.tape[self.cell] = ascii_index

    def generate_action_dict(self) -> dict[str, Callable[[], None]]:
        """
        Generates the action dictionary, mapping each Brainfuck command
        to a corresponding action to be executed while running the program
        """
        return {
            "+": self.increment,
            "-": self.decrement,
            ">": self.go_right,
            "<": self.go_left,
            "[": self.start_loop,
            "]": self.finish_loop,
            ".": self.print,
            ",": self.read,
        }

    def generate_bracket_dict(self) -> dict[int, int]:
        """
        Generates a dictionary of bracket positions for the brainfuck program.
        When a bracket [ starts at position i and ends with ] at position j,
        the dictionary has i -> j as well as j -> i. This facilitates jumping
        between the bracket positions when running the interpreter.

        Returns:
            The bracket dictionary

        Raises:
            SyntaxError: When the brackets do not match up
        """
        bracket_dict: dict[int, int] = {}
        opening_bracket_positions = []
        for pos, char in enumerate(self.program):
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

    def run(self) -> None:
        """Runs the Brainfuck interpreter"""
        if self.debug:
            print("program:", self.program)

        while self.pos < len(self.program):
            char: str = self.program[self.pos]

            if not char in BrainfuckInterpreter.ALLOWED_CHARS:
                self.pos += 1
                continue

            if self.debug:
                tape_with_pos = ", ".join(
                    str(val) if i != self.cell else f"|{str(val)}|"
                    for i, val in enumerate(self.tape)
                )
                print("tape:", tape_with_pos)
                print("char:", char)

            action = self.actions[char]
            action()
            self.pos += 1


def main() -> None:
    """
    Reads the file passed as an argument, creates a brainfuck
    interpreter for it and executes it.
    """
    args = sys.argv
    if len(args) == 1:
        raise ValueError("Missing file path")
    file_path = sys.argv[1]
    debug = len(args) == 3 and args[2] == "debug"
    with open(file_path, "r", encoding="utf8") as file:
        program = file.read()
        interpreter = BrainfuckInterpreter(program, debug)
        interpreter.run()


if __name__ == "__main__":
    main()
