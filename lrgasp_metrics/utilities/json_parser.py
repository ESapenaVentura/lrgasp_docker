#!/usr/bin/env python

import json

def json_parser( experiment):
    e = open(experiment , "r")
    experiment_json = json.load(e)
    exp_id = experiment_json["experiment_id"]
    p = experiment_json["platforms"]
    if len(p)>1:
        platforms = '+'.join(p)
    else:
        platforms = p[0]
    ent_id = f"LRGASP_{experiment_json['experiment_id']}_{experiment_json['software']['name'].lower()}"
    return exp_id, ent_id, platforms
