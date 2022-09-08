# lrgasp_docker

### How to run

- Make sure you have installed docker
- Clone this repository
- Go to the root of this repository
- Run:
    ```
    sh build.sh 1.0.0
    ```
  This will build the docker images needed to run the three steps, with the 1.0.0 tag (default)
    ```
    sh pipeline.bash
    ```
  Since we have not set up any parameters yet, it will print a usage statement:
    ```
    Usage: pipeline.bash input_dir gtf_filename input_cage_peak input_polyA entry_json experiment_json coverage_filename results_dir
    When running, please ensure all the needed files are in the input_dir, and give filenames for the rest of the files. The output dir must also be a full path
    ```
- Re-run now, but adding the parameters specified in the previous bullet point. This will execute the whole pipeline, and all the results will be output to the results_dir

**Note**: the "lrgasp_metrics" step executes sqanti3, a tool that requires at least 3 GB of ram memory allocation. Please ensure that your docker is configured to allow at least 3 GB of ram memory for the containers.

## Addendum
### Changes to sqanti3
- all `sys.exit(-1)` replaced with `sys.exit(1)`.


