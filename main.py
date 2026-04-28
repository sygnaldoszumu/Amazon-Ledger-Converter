from amazon_ledger_converter.path_validation import *
from amazon_ledger_converter.extration import *
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()

    validators = [path_exists(), non_empty_file()]

    if args.file:
        if error := validate_chain(validators, args.file):
            sys.exit(error)
        file_path = args.file
    else:
        file_path = prompt_for_file(validators)

    print(read_csv(file_path))

    


if __name__ == "__main__":
    main()
