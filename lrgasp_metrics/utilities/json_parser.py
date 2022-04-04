#!/usr/bin/env python3

import json


def json_parser(experiment: str, entry: str) -> (str, str, str):
    with open(experiment, "r") as e:
        experiment_json = json.load(e)
    with open(entry, "r") as f:
        entry_json = json.load(f)

    exp_id = experiment_json.get('experiment_id', "")
    platforms = "+".join(experiment_json.get('platforms', ""))
    ent_id = entry_json["entry_id"]

    return exp_id, ent_id, platforms
