import os
from collections.abc import Callable

FileValidator = Callable[[str], str | None]  # returns error string or None

#########################################################
# Using factories here for easier testing/extensibility #
#########################################################

def path_exists(exists_fn=None):
    check = exists_fn if exists_fn is not None else os.path.exists
    def validate(path: str) -> str | None:
        return None if check(path) else f"No file at: {path}"

    return validate


def non_empty_file(getsize_fn=None):
    check = getsize_fn or os.path.getsize
    def validate(path: str) -> str | None:
        return None if check(path) > 0 else f"File is empty: {path}"
    return validate


def validate_chain(validators: list[FileValidator], path: str) -> str | None:
    return next((err for v in validators if (err := v(path))), None)


def prompt_for_file(validators: list[FileValidator], prompt_fn=input) -> str:
    while True:
        path = prompt_fn("Enter file path: ").strip()
        if error := validate_chain(validators, path):
            print(error)
        else:
            return path



def make_file_prompt(
    label: str,
    validators: list[FileValidator],
    prompt_fn: Callable[[str], str] = input,
) -> Callable[[], str]:
    def prompt_for_file() -> str:
        while True:
            path = prompt_fn(f"Enter {label} file path: ").strip()

            if error := validate_chain(validators, path):
                print(error)
                continue

            return path

    return prompt_for_file
