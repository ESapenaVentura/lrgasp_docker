import os
from jsonschema import *
import json
import argparse

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
ERRORS = []

def full_path_dir(path: str):
    if not os.path.isabs(path) and not os.path.isdir(path):
        raise ValueError("Provided path is not a full path")
    return path

def is_file(path: str) -> str:
    if not os.path.isfile(path):
        raise ValueError("Provided path is not pointing to any file")
    return path



def parse_arguments(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument("-c", "--cage-peak", help="CAGE-PEAK file path", required=True, type=is_file)
    parser.add_argument("-p", "--polya-list", help="Poly-A motif list", required=True, type=is_file)
    parser.add_argument("-e", "--entry", help="Entry JSON document", required=True, type=is_file)
    parser.add_argument("-s", "--schemas-path", help="Path to the JSON schemas", required=False,
                        default=f"{SCRIPT_PATH}/JSON_TEMPLATES", type=full_path_dir)
    args = parser.parse_args()
    return args


def schemas_are_in_path(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if "contacts.json" not in files or "entry_schema.json" not in files:
        return False
    return True


def main(cage_peak_path, poly_a_path, entry_path: str, schemas_path: str):
    # Validation step 1: Ensure all schemas are stored in the path provided
    if not schemas_are_in_path(schemas_path):
        ERRORS.append("Couldn't find schemas in the directory provided")

    print(ERRORS)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parse_arguments(parser)
    main(args.cage_peak, args.polya_list, args.entry, args.schemas_path)

"""
with open("../Example/entry.json", "r") as f:
    entry = json.load(f)

with open("JSON_TEMPLATES/entry_schema.json", "r") as f:
    schema = json.load(f)


resolver = RefResolver(SCRIPT_PATH + "\\JSON_TEMPLATES\\", schema)
validator = Draft7Validator(schema, resolver)

try:
    errors = sorted(validator.iter_errors(entry), key=lambda e: e.path)
except RefResolutionError as e:
    print(e)
"""