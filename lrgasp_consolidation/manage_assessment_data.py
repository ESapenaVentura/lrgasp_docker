#!/usr/bin/env python3

from __future__ import division
import requests
import json
import os
import logging
import sys
from argparse import ArgumentParser
import datetime

# TODO change eventmarks
# TODO ADD OEB IDENTIFIERS FOR DIFFERENT METRICS
DEFAULT_eventMark = datetime.date.today()
DEFAULT_OEB_API = "https://dev-openebench.bsc.es/api/scientific/graphql"
DEFAULT_eventMark_id = "OEBE0010000000"
METRICS =  {"precision":"OEBM0010000001", "TPR": "OEBM0010000002"}

def main(args):

    # input parameters
    data_dir = args.benchmark_data
    participant_path = args.participant_data
    output_dir = args.output
    offline = args.offline
    
    # Assuring the output directory does exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # read participant metrics
    participant_data = read_participant_data(participant_path)
    if offline is None:
        response = query_OEB_DB(DEFAULT_eventMark_id)
        getOEBAggregations(response, data_dir)
    generate_manifest(data_dir, output_dir, participant_data)

    # Distinct metrics are divided by the match type, so we need to do this
    WANTED_METRICS = [['5_reference_supported_(transcript)', '5_cage_supported'], ['3_reference_supported_(transcript)', '3_quantseq_supported']]
    match_types = ["FSM", "ISM", "NIC", "NNC"]
    ALL_COMBINATIONS = []
    for metric_comb in WANTED_METRICS:
        for sq_class in match_types:
            ALL_COMBINATIONS.append([f"{metric}_%" for metric in metric_comb])


    for challenge_name in participant_data.keys():
        for y_metric_name, x_metric_name in ALL_COMBINATIONS:
            generate_manifest_2d_plots(data_dir, challenge_name, output_dir, y_metric_name, x_metric_name)
    sys.exit(0)



def generate_manifest_2d_plots(data_dir, challenge_name, output_dir, y_metric_name, x_metric_name):
    """
    This function takes advantage of the already existing JSON files to generate the 2d plots more easily.

    :param data_dir:
    :param output_dir:
    :param y_metric_name:
    :param x_metric_name:
    :return:
    """
    x_metric_file = None
    y_metric_file = None
    for file in os.listdir(os.path.join(output_dir, challenge_name)):
        if file == f"{challenge_name}_{x_metric_name}.json":
            x_metric_file = file
        if file == f"{challenge_name}_{y_metric_name}.json":
            y_metric_file = file
    else:
        # Safeguarding against possible missing metrics
        if not x_metric_file or not y_metric_file:
            return

    # Load metrics
    metric_Y = json.load(open(os.path.join(output_dir, challenge_name, y_metric_file), 'r'))
    metric_X = json.load(open(os.path.join(output_dir, challenge_name, x_metric_file), 'r'))



    # Re-build aggregation for comparison metrics based on individual aggregation files
    challenge_participants = []
    for y_challenge_participants in metric_Y['datalink']['inline_data']['challenge_participants']:
        for x_challenge_participants in metric_X['datalink']['inline_data']['challenge_participants']:
            if y_challenge_participants['participant_id'] == x_challenge_participants['participant_id']:
                challenge_participants.append({"metric_y": y_challenge_participants['metric_y'],
                     "metric_x": x_challenge_participants['metric_y'],
                     "participant_id": y_challenge_participants['participant_id']
                })


    # Reasoning behind not checking aggregation file is that this is being built on already aggregated data -
    # There should be no instance of a comparison metric (x vs y) to exist without it existing individually in the x_metric and y_metric files
    aggregation_file = {
        "_id": "LRGASP:{}_{}_Aggregation".format(DEFAULT_eventMark, challenge_name),
        "challenge_ids": [
            challenge_name
        ],
        "datalink": {
            "inline_data": {
                "challenge_participants": challenge_participants,
                "visualization": {
                    "type": "2D-plot",
                    "x_axis": x_metric_name,
                    "y_axis": y_metric_name
                }
            }
        },
        "type": "aggregation"
    }
    summary_dir = os.path.join(output_dir, challenge_name, f"{challenge_name}_{y_metric_name}_{x_metric_name}.json")

    with open(summary_dir, 'w') as f:
        json.dump(aggregation_file, f, sort_keys=True, indent=4, separators=(',', ': '))



##get existing aggregation datasets for that challenges
def query_OEB_DB(bench_event_id):
    json_query = {'query': """query AggregationQuery($bench_event_id: String) {
    getChallenges(challengeFilters: {benchmarking_event_id: $bench_event_id}) {
        _id
        acronym
        metrics_categories{
          metrics {
            metrics_id
            orig_id
          }
        }
        datasets(datasetFilters: {type: "aggregation"}) {
                _id
                _schema
                orig_id
                community_ids
                challenge_ids
                datalink {
                    inline_data
                }
        }
    }
}""",
                'variables': {
                    'bench_event_id': bench_event_id
                }
            }
    try:
        url = DEFAULT_OEB_API
        # get challenges and input datasets for provided benchmarking event
        r = requests.post(url=url, json=json_query, headers={'Content-Type': 'application/json'})
        response = r.json()
        data = response.get("data")
        if data is None:
            logging.fatal("For {} got response error from graphql query: {}".format(bench_event_id, r.text))
            sys.exit(6)
        if len(data["getChallenges"]) == 0:
            logging.fatal("No challenges associated to benchmarking event " + bench_event_id +
                          " in OEB. Please contact OpenEBench support for information about how to open a new challenge")
            sys.exit()
        else:
            return data.get('getChallenges')
    except Exception as e:

        logging.exception(e)
        
# function to populate bench_dir with existing aggregations
def getOEBAggregations(response, output_dir):
    for challenge in response:
        
        challenge['datasets'][0]['datalink']["inline_data"] = json.loads(challenge['datasets'][0]["datalink"]["inline_data"])
        
        for metrics in challenge['metrics_categories'][0]['metrics']:
            if metrics['metrics_id'] == challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["x_axis"]:
                challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["x_axis"] = metrics['orig_id'].split(":")[-1]
            elif metrics['metrics_id'] == challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["y_axis"]:
                challenge['datasets'][0]['datalink']["inline_data"]["visualization"]["y_axis"] = metrics['orig_id'].split(":")[-1]
        
        # replace tool_id for participant_id (for the visualitzation)
        for i in challenge['datasets'][0]['datalink']['inline_data']['challenge_participants']:
            i["participant_id"] = i.pop("tool_id")
        
        new_aggregation = {
            "_id": challenge['datasets'][0]['_id'],
            "challenge_ids": [
                 challenge['acronym']
            ],
            'datalink': challenge['datasets'][0]['datalink']
        }
        with open(os.path.join(output_dir, challenge['acronym']+".json"), mode='w', encoding="utf-8") as f:
            json.dump(new_aggregation, f, sort_keys=True, indent=4, separators=(',', ': '))
        
        
        
         
    

def read_participant_data(participant_path):
    participant_data = {}

    with open(participant_path, mode='r', encoding="utf-8") as f:
        result = json.load(f)
        if isinstance(result, list):
            for item in result:
                participant_data.setdefault(item['challenge_id'], []).append(item)
        else:
            participant_data.setdefault(result['challenge_id'], []).append(result)

    return participant_data


def generate_manifest(data_dir,output_dir, participant_data):

    info = []
    """
    For each of the challenge_id defined:
    - Create a path with `output_dir/challenge_id`
    If the path already contains data for that challenge, aggregate it
    if not, create it 
    """
    for challenge_id, metrics_file in participant_data.items():
        challenge_dir = os.path.join(output_dir, challenge_id)
        if not os.path.exists(challenge_dir):
            os.makedirs(challenge_dir)
        participants = []


        pre_aggregation_file = {}
        for m in metrics_file:
            metric_Y = m["metrics"]["metric_id"]
            lrgasp_oeb_data_dir = os.path.join(os.path.join(data_dir, challenge_id), f"{challenge_id}_{metric_Y}")
            lrgasp_oeb_data = lrgasp_oeb_data_dir + ".json"
            if os.path.isfile(lrgasp_oeb_data):
                # Transferring the public participants data
                with open(lrgasp_oeb_data, 'r') as f:
                    aggregation_file = json.loads(f.read())
                pre_aggregation_file[metric_Y] = aggregation_file

            # get default id for metric in y axis
            challenge_participants = {"metric_y": m['metrics']['value'],
                                      "participant_id": m['participant_id']}


            if metric_Y not in pre_aggregation_file:
                pre_aggregation_file[metric_Y] = {
                    "_id": "LRGASP:{}_{}_Aggregation".format(DEFAULT_eventMark, challenge_id),
                    "challenge_ids": [
                        challenge_id
                    ],
                    "datalink": {
                        "inline_data": {
                            "challenge_participants": [],
                            "visualization": {
                                "type": "bar-plot",
                                "y_axis": metric_Y
                            }
                        }
                    },
                    "type": "aggregation"
                }
            pre_aggregation_file[metric_Y]['datalink']['inline_data']['challenge_participants'].append(challenge_participants)


        #copy the updated aggregation file to output directory
        for metrics_name, aggregation_file in pre_aggregation_file.items():
            summary_dir = os.path.join(challenge_dir, f"{challenge_id}_{metrics_name}.json")

            with open(summary_dir, 'w') as f:
                json.dump(aggregation_file, f, sort_keys=True, indent=4, separators=(',', ': '))


                # add the rest of participants to manifest
            for name in aggregation_file["datalink"]["inline_data"]["challenge_participants"]:
                participants.append(name["participant_id"])
                participants = list(set(participants))

        #generate manifest
        obj = {
            "id" : challenge_id,
            "participants": participants,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
        }

        info.append(obj)

    with open(os.path.join(output_dir, "Manifest.json"), mode='w', encoding="utf-8") as f:
        json.dump(info, f, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-p", "--participant_data", help="path where the data for the participant is stored", required=True)
    parser.add_argument("-b", "--benchmark_data", help="dir where the data for the benchmark will be or is stored", required=True)
    parser.add_argument("-o", "--output", help="output directory where the manifest and output JSON files will be written", required=True)
    parser.add_argument("--offline", help="offline mode; existing benchmarking datasets will be read from the benchmark_data", required=False, type= bool)
    args = parser.parse_args()

    main(args)
