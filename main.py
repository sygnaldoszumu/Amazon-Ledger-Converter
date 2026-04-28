from amazon_ledger_converter.path_validation import * 
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")  # optional positional
    args = parser.parse_args()

    validators = [path_exists(), non_empty_file()]

    if args.file:
        if error := validate_chain(validators, args.file):
            sys.exit(error)
        return args.file
    else:
        return prompt_for_file(validators)

    


if __name__ == "__main__":
    main()
