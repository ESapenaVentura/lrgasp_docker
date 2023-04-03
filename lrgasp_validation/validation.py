"""
Validation that is performed:

- All files exist in the path provided
- Schemas path is absolute
- There are json files in the schemas_path
- Entry metadata is validated against schema

#TODO
- More tests from lrgasp-tools applied
- Requiring entry + experiment.json may be an overkill

"""

import os
import sys
import json
import argparse
import hashlib
from jsonschema import RefResolver, Draft7Validator

# lrgasp-tools validation
from lrgasp import model_data
from lrgasp import read_model_map_data
from lrgasp.entry_validate import validate_ref_model_and_read_mapping

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
    parser.add_argument("-i", "--input-path", help="Input path where all the files are stored", required=True)
    parser.add_argument("-e", "--entry", help="Entry JSON document", required=True)
    parser.add_argument("-x", "--experiment", help="Experiment JSON document", required=True)
    parser.add_argument("-s", "--schemas-path", help="Path to the JSON schemas", required=False,
                        default=f"{SCRIPT_PATH}/JSON_TEMPLATES", type=full_path_dir)
    parser.add_argument("-o", "--output-path", help="Output directory", required=True, type=str)
    parser.add_argument("-g", "--gtf-filename", help="GTF filename", required=True, type=str)
    parser.add_argument("-r", "--read-model-map-filename", help="Read model map data filename", required=True, type=str)
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
        if checked_md5.get(file, '') != md5_map.get(file,''):
            ERRORS.append(f"MD5 checksum failed for file {file}.")





def main(input_path:str, entry_name: str, experiment_name: str, schemas_path: str, output: str, gtf_filename:str,
         read_model_map_filename:str):

    entry_path = os.path.join(input_path, entry_name)
    experiment_path = os.path.join(input_path, experiment_name)
    gtf_path = os.path.join(input_path, gtf_filename)
    read_model_map_path = os.path.join(input_path, read_model_map_filename)

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

    # TODO: Add option to programmatically download reference genome and transcriptome
    # Files are big and therefore they should be either: provided or downloaded (Can allow both)


    # Validation step 2: Ensure contents are ok

    # Validate ref model experiment
    try:
        models = model_data.load(gtf_path)
        read_model_map = read_model_map_data.load(read_model_map_path)
        validate_ref_model_and_read_mapping(models, read_model_map)
    except Exception as ex:
        ERRORS.append(f"Error found during ref model experiment validation: {ex}")

    # TODO: apply more tests from https://github.com/LRGASP/lrgasp-submissions/tree/master/tests


    # Validation step 3: Generate participant dataset
    # To generate the participant datasets, we will be using the example code from https://github.com/inab/TCGA_benchmarking_dockers

    data_id = f"LRGASP_{experiment['experiment_id']}_{entry['team_name']}"
    validated = False if ERRORS else True
    challenges = [f"iso_detect_ref_{e}" for e in entry['experiment_ids']]
    output_json = JSON_templates.write_participant_dataset(data_id, "OEBC010", challenges, experiment['software'][0]['name'].lower(),
                                                           validated)
    with open(output, 'w') as f:
        json.dump(output_json, f, sort_keys=True, indent=4, separators=(',', ': '))



    if not ERRORS:
        sys.exit(0)
    else:
        formatted_errors = "\n\t- ".join(ERRORS)
        sys.exit(f"ERROR: Submitted data does not validate! The following errors were found: \n\t- {formatted_errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parse_arguments(parser)
    main(args.input_path, args.entry, args.experiment, args.schemas_path, args.output_path, args.gtf_filename, args.read_model_map_filename)