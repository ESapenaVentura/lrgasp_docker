# lrgasp docker containers repository

## Purpose of this repository

This repository has been created to hold the containers used for the challenge 1 of the [OpenEBench's implementation](https://openebench.bsc.es/benchmarking/OEBC010) of [LRGASP](https://www.gencodegenes.org/pages/LRGASP/).

This repository updates the container registry used by OEB on release, allowing for several commits and pushes before a new version is released. 3 repositories are used:
- [Validation step](https://hub.docker.com/repository/docker/lrgaspdocker/validation_challenge_1/)
- [Metrics step](https://hub.docker.com/repository/docker/lrgaspdocker/metrics_challenge_1/)
- [Consolidation step](https://hub.docker.com/repository/docker/lrgaspdocker/consolidation_challenge_1/)

Following the [TCGA Benchmarking dockers](https://github.com/inab/TCGA_benchmarking_dockers) example.


## Repository structure

![OEB](https://openebench.readthedocs.io/en/latest/_images/workflow_schema.jpg)
(Extracted from OEB's documentation page, https://openebench.readthedocs.io/en/latest/technical_references/4_benchmarking_workflows.html)

The structure of this repository follows the main structure as described in [OEB specification page](https://openebench.readthedocs.io/en/latest/how_to/4_manage_events.html#how-to-prepare-a-benchmarking-event).

The specifics of this repository are described in the following subsections

### Root

- build.sh: This file, when run, will build the docker images for the validation, metrics and consolidation step. The tag provided (e.g. `1.0.0`) needs to be the same as to when the pipeline is executed.
- pipeline.bash: When run and given the proper tag id's, will execute the whole pipeline.

### data
Contains the full data for LRGASP challenge 1.

### example_data
This folder contains all the necessary files to run the `pipeline.bash` script. They belong to a real example. The IDs have been anonymised. To know how to used this data, please refer to the `How to run` section

### lrgasp_validation
This folder contains the scripts necessary for the validation step of the benchmark.

### lrgasp_metrics
This folder contains the scripts necessary for the metrics step of the benchmark.

Sqanti3 is being used here to generate the reports.

### lrgasp_consolidation
This folder contains the scripts necessary for the consolidation step of the benchmark.

### How to run

- Make sure you have installed docker
- Clone this repository
- Go to the root of this repository
- Download the missing files: The reference transcriptome and genome following the instructions [here](https://lrgasp.github.io/lrgasp-submissions/docs/reference-genomes.html)
- Run:
    ```
    sh build.sh 0.5.1
    ```
  (If other versions are specified, please change it for the execution of pipeline.bash)
  This will build the docker images needed to run the three steps, with the 0.5.1 tag 
    ```
    sh pipeline.bash
    ```
  Since we have not set up any parameters yet, it will print a usage statement:
    ```
    Usage: pipeline.bash input_dir gtf_filename input_cage_peak input_polyA entry_json experiment_json coverage_filename results_dir
    When running, please ensure all the needed files are in the input_dir, and give filenames for the rest of the files. The output dir must also be a full path
    ```
- Re-run now, but adding the parameters specified in the previous bullet point. This will execute the whole pipeline, and all the results will be output to the results_dir. An example run with the example data:
   ```bash
   sh pipeline.bash example_data/iso_detect_ref_input_example models.gtf mouse.refTSS_v3.1.mm39.bed polyA_list.txt entry.json experiment.json lrgasp_grcm39_sirvs.fasta lrgasp_gencode_vM28_sirvs.mouse.gtf SJ.out.tab example_data/iso_detect_ref_output_example 1.0.0 read_model_map.tsv
   ```

### Testing steps individually

If you are interested in contributing to the repo, you can test changes to each of the steps individually by building a docker image for any of the steps (folders). An example with the validation step, after making the desired changes:
```bash
docker build -t "lrgasp_validation":"0.5.1" "lrgasp_validation"
docker run --rm -u $UID -v "example_data":/app/input:ro -v "example_output":/app/output lrgasp_validation:"0.5.1" \
	   -e /app/input/entry.json -x /app/input/experiment.json
```

Please note:

1. Each of the steps require a different set of inputs; for some information on what inputs they require, you can run the docker image without any arguments or take a look at the pipeline.bash script
2. Please ensure that the outputs are still valid; depending on the steps, a set of outputs is required by the next step

### Common errors FAQ
> The pipeline dies after some time executing. What is happening?

The "lrgasp_metrics" step executes sqanti3, a tool that requires at least 3 GB of ram memory allocation for this challenge. Please ensure that your docker is configured to allow at least 3 GB of ram memory for the containers.
If after allocating more memory it keeps dying, please feel free to open a ticket and we will look into it.


## Addendum

### How to contribute

If you want to contribute by improving the code, feel free to open PRs! Just remember to please update indirectly affected files - That accounts for:
- This README file: Anything that changes inputs or outputs on runtime should be taken into account here
- The example_data folder README file: Again, there is a comprehensive list of inputs and outputs there - Please update if modified.
- The requirements.txt: To modify them, we use `pip-compile`, which takes into account the dependencies of your project dependencies to create a perfectly reproducible requirements file. To use, run this in the root of the repo:
   ```bash
  pip3 install pip-tools==6.13.0
   ```
  within your console or a set-up virtual environment. This will install pip-compile, which is used to transform requirements.in ("Raw" requirements files) into requirements.txt ("Dependency-thorough" requirement files). To use, just update the `requirements.in` file and, in the same folder, run `python3 -m piptools compile`

### Changes to sqanti3
- all `sys.exit(-1)` replaced with `sys.exit(1)`.


