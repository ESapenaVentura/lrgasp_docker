import sys
import os

import pyreadr
import json
import jsonschema


def read_rdata(path):
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

def metric_to_filename(metric):
    metric = metric.replace("'", "").replace(' ', "_").lower()
    return metric

def main(experiment_path, rdata_path, output_path, challenge):
    match = challenge.split("_")[1].replace('sirvs', 'SIRV')
    # Set the values to pass to write_assessment_dataset contained in experiment metadata
    experiment = json.load(open(experiment_path, 'r'))
    community = "OEBC010"
    challenge_id = challenge

    # Set the value for the participant id (from experiment.json). Each participant ID is the name of the tool they used to analyse the data
    participant_name = experiment['software']['name'].lower()

    # Set the metric values obtained from sqanti
    fsm_results = read_rdata(rdata_path)
    metric_ids = ["Reference Match", "5' reference supported (transcript)",
                  "3' reference supported (transcript)", "5' CAGE supported",
                  "3' polyA supported",
                  "Supported Reference Transcript Model (SRTM)",
                  "Intra-priming"]

    # Need to adjust, looking for different metrics for Spike-ins (Known transcripts) vs sqanti-calculated matches
    metric_ids = metric_ids if "SIRV" not in match else ["Sensitivity", "Precision", "Non Redundant Precision", "Positive Detection Rate", "False Discovery Rate", "False Detection Rate"]
    for metric_id in metric_ids:
        value_type = 'Value' if "SIRV" in match else 'Relative value (%)'
        percentage = "" if "SIRV" in match else "_%"
        try:
            metric_value = float(fsm_results[f'{match}_only'][value_type].get(metric_id))
        except TypeError or ValueError:
            # When the value is None (Metric does not exist) or was not calculated (May be represented as NA)
            metric_value = None
        if not metric_value:
            continue
        error = 0
        metric_id = f"{metric_to_filename(metric_id)}{percentage}"
        experiment_id = f"{community}:{challenge_id}_{metric_id}_{participant_name}"
        # Write and validate results
        assessment_dataset = create_assessment_dataset(experiment_id, community, challenge_id, participant_name, metric_id, metric_value, error)
        if os.path.exists(output_path):
            existing_assesment = json.load(open(output_path, 'r'))
            existing_assesment.append(assessment_dataset)
        else:
            existing_assesment = [assessment_dataset]
        with open(output_path, 'w') as f:
            json.dump(existing_assesment, f, indent=4, separators=(', ', ": "))



if __name__ == "__main__":
    main()