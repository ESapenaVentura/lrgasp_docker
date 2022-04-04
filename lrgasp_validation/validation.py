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
import sys
import json
import argparse
import hashlib
from jsonschema import RefResolver, Draft7Validator
from pprint import pprint

import JSON_templates

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
    parser.add_argument("-x", "--experiment", help="Experiment JSON document", required=True, type=is_file)
    parser.add_argument("-s", "--schemas-path", help="Path to the JSON schemas", required=False,
                        default=f"{SCRIPT_PATH}/JSON_TEMPLATES", type=full_path_dir)
    args = parser.parse_args()
    return args


def schemas_are_in_path(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if "experiment.json" not in files or "entry.json" not in files:
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


def validate_schemas(schema_store, schemas_path, entry, experiment):
    # Build the reference resolver and the validators
    resolver = RefResolver(referrer=schema_store, base_uri=f"file://{schemas_path}/")
    validator_entry = Draft7Validator(schema_store.get('entry.json'), resolver=resolver)
    experiment_entry = Draft7Validator(schema_store.get('experiment.json'), resolver=resolver)

    # Iterate the errors and append them to our error log
    for error in validator_entry.iter_errors(entry):
        ERRORS.append(f"Value {error.message}")
    for error in experiment_entry.iter_errors(experiment):
        ERRORS.append(f"Value {error.message}")


def validate_bed_file(bed_path):
    """
    Read the bed file and check for:
        - BED file contains at least 3 columns separated by tabs
        - All rows have the same number of columns (size)
    :param bed_path: Path to the CAGE-peaks BED file
    :return:
    """
    with open(bed_path, "r") as f:
        bed = f.readline().split('\t')
        row_one_length = len(bed)
        i = 1
        if len(bed) == 1:
            ERRORS.append(f"CAGE-peaks file columns should be separated by tabs. File used: {bed_path}")
        elif len(bed) < 3:
            ERRORS.append(f"CAGE-peaks file should contain at least 3 columns. File used: {bed_path}")
        else:
            if not all(len(line.split('\t')) == row_one_length for line in f):
                ERRORS.append(f"CAGE-peaks file should have the same amount of columns per row. File used: {bed_path}")


def get_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_md5_files(md5_list_path:str = "static_md5_list.txt"):
    static_md5_map = {}
    with open(md5_list_path, 'r') as f:
        content = f.read().splitlines()
        static_md5_map = {line.split("(")[1].split(") = ")[0]: line.split("(")[1].split(") = ")[1] for line in content}
    return static_md5_map

def check_static_checksums(static_folder):
    files = [f for f in os.listdir(static_folder) if os.path.isfile(os.path.join(static_folder, f))]
    md5_map = {f: get_md5(os.path.join(static_folder, f)) for f in files}
    checked_md5 = read_md5_files()
    for file in md5_map.keys():
        if checked_md5[file] != md5_map[file]:
            ERRORS.append(f"MD5 checksum failed for file {file}.")





def main(cage_peak_path, poly_a_path, entry_path: str, experiment_path: str, schemas_path: str):

    # Validation step 1: Schemas
    # Validation step 1.1: Ensure all schemas are stored in the path provided
    if not schemas_are_in_path(schemas_path):
        ERRORS.append(f"Couldn't find schemas in the directory provided: {schemas_path}")

    # Validation step 1.2: Load schema files as an store
    store = load_schemas_store(schemas_path)

    # Validation step 1.3: Load user entry and experiment instances
    entry = json.load(open(entry_path, "r"))
    experiment = json.load(open(experiment_path, "r"))

    # Validation step 1.4: Validate metadata schema against instances provided
    validate_schemas(store, schemas_path, entry, experiment)

    # Validation step 2: Ensure static files are ok
    validate_bed_file(cage_peak_path)
    check_static_checksums("../input_files/static")
    # TODO: Add option to programmatically download reference genome and transcriptome
    # Files are big and therefore they should be either: provided or downloaded (Can allow both)


    # Validation step 3: Ensure contents are ok
    # TODO: Check with Fran what validation was performed on the files


    # Validation step 4: Generate participant dataset
    # To generate the participant datasets, we will be using the example code from https://github.com/inab/TCGA_benchmarking_dockers
    #  TODO: Check if we want to use other parameters for metadata in participant dataset

    data_id = f"LRGASP_{experiment['experiment_id']}_{entry['team_name']}"
    validated = False if ERRORS else True
    output_json = JSON_templates.write_participant_dataset(data_id, "LRGASP", entry['challenge_id'], entry['team_name'],
                                                           validated)
    with open("participant.json" , 'w') as f:
        json.dump(output_json, f, sort_keys=True, indent=4, separators=(',', ': '))



    if not ERRORS:
        sys.exit(0)
    else:
        formatted_errors = "\n\t- ".join(ERRORS)
        sys.exit(f"ERROR: Submitted data does not validate! The following errors were found: \n\t- {formatted_errors}")
    pprint(ERRORS)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parse_arguments(parser)
    main(args.cage_peak, args.polya_list, args.entry, args.experiment, args.schemas_path)