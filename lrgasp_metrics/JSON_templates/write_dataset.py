import sys
import os

import pyreadr
import json
import jsonschema


def read_rdata(path = '/Users/enrique/HumanCellAtlas/lrgasp_docker/Example/ES_cdna_pacbio_ls/SQANTI_output/models_Rdata/ES_cdna_pacbio_ls_FSM_results.RData'):
    return pyreadr.read_r(path)


"""
    Assessment datasets should be generated in the METRICS COMPUTATION step
    The minimal required properties for this dataset are:
    - ID - the id assigned to this dataset by the community
    - community - the benchmarking community name/OEB-id
    - challenge - the challenge where the metrics were computed
    - participant_name - name/OEB-id of the tool which is evaluated in this assessment
    - metric - the name of the unique metric which correspond to this assessment
    - metric_value - the numeric value of the metric
    - error - the standard error/deviation for the computed metric (can be 0)
"""
def create_assessment_dataset(ID, community, challenge, participant_name, metric, metric_value, error):

    data = {
        "_id": ID,
        "community_id": community,
        "challenge_id": challenge,
        "type": "assessment",
        "metrics": {"metric_id": metric,
                    "value": float(metric_value),
                    "stderr": error
                    },
        "participant_id": participant_name

    }

    # validate the generated object with the minimal JSON schema

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Benchmarking_minimal_datasets_schema.json'), 'r') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(data, schema)
        return data

    except jsonschema.exceptions.ValidationError as ve:
        sys.stderr.write(
            "ERROR: JSON schema validation failed. Output json file does not have the correct format:\n" + str(
                ve) + "\n")


def main(experiment_path, entry_path, rdata_path, output_path):
    # Set the values to pass to write_assessment_dataset contained in experiment metadata
    experiment = json.load(open(experiment_path, 'r'))
    # TODO must be unique
    experiment_id = experiment['experiment_id']
    community = "LRGASP"
    challenge_id = f"{experiment['challenge_id']}_{experiment['experiment_id']}"

    # Set the value for the participant id (from entry.json)
    entry = json.load(open(entry_path, "r"))
    participant_name = entry['team_name']

    # Set the metric values obtained from sqanti
    # TODO: check how many metrics per assessment dataset
    fsm_results = read_rdata(rdata_path)
    metric_id = "Reference Match"
    metric_value = fsm_results['FSM_only'].loc['Reference Match']['Relative value (%)']
    error = 0  # TODO: check if stderr is 0 or we can give a value

    # Write and validate results
    assessment_dataset = create_assessment_dataset(experiment_id, community, challenge_id, participant_name, metric_id, metric_value, error)
    with open(f'{output_path}', 'w') as f:
        json.dump(assessment_dataset, f, indent=4, separators=(', ', ": "))



if __name__ == "__main__":
    main()