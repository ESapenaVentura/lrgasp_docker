import os
from jsonschema import *
import json

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

print(SCRIPT_PATH)

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
