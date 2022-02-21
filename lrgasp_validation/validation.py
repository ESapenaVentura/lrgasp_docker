"""
Validation that is performed:

- All files exist in the path provided
- Schemas path is absolute
- There are json files in the schemas_path
- Entry metadata is validated against schema

#TODO
- Schemas are valid JSON SCHEMAS
- Experiment metadata is validated against schema
- Bed file has proper formatting (Check with pybedtools)

"""

import os
import json
import argparse
from jsonschema import RefResolver, Draft7Validator
from pybedtools import BedTool

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


def load_schemas_store(schemas_path: str) -> dict:
    files = [f for f in os.listdir(schemas_path) if os.path.isfile(os.path.join(schemas_path, f))]
    schemas = []
    for f in files:
        try:
            schemas.append(json.load(open(f"{schemas_path}/{f}", 'r')))
        except:
            ERRORS.append(f"Could not load {f}, not a recognised JSON entity")
    # Transform schemas loaded into store
    store = {schema['$id']: schema for schema in schemas}
    return store


def validate_schemas(schema_store, schemas_path, entry):
    # Build the reference resolver and the validators
    resolver = RefResolver(referrer=schema_store, base_uri=f"file://{schemas_path}/")
    validator_entry = Draft7Validator(schema_store.get('entry.json'), resolver=resolver)

    # Iterate the errors and append them to our error log
    for error in validator_entry.iter_errors(entry):
        ERRORS.append(f"Value {error.message}")


def validate_bed_file(bed_path):
    with open(bed_path, "r") as f:
        bd = f.read()
    bed = BedTool(bd, from_string=True)
    try:
        ft = bed.file_type
        if ft == 'empty':
            ERRORS.append("Bed file is empty")
    except IndexError:
        print("miau")
        ERRORS.append('Bed file is corrupted/Does not have proper formatting')


def main(cage_peak_path, poly_a_path, entry_path: str, schemas_path: str):

    # Validation step 1: Schemas
    # Validation step 1.1: Ensure all schemas are stored in the path provided
    if not schemas_are_in_path(schemas_path):
        ERRORS.append(f"Couldn't find schemas in the directory provided: {schemas_path}")

    # Validation step 1.2: Load schema files as an store
    store = load_schemas_store(schemas_path)

    # Validation step 1.3: Load user entry and experiment instances
    entry = json.load(open(entry_path, "r"))

    # Validation step 1.4: Validate metadata schema against instances provided
    validate_schemas(store, schemas_path, entry)
    #TODO ADD EXPERIMENT INSTANCE

    # Validation step 2: Ensure static files are ok
    validate_bed_file(cage_peak_path)

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