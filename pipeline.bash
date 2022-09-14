#!/bin/sh

#Run the SQANTI3 pipeline
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}


REALPATH="$(realpath "$0")"
BASEDIR="$(dirname "$REALPATH")"
case "$BASEDIR" in
	/*)
		true
		;;
	*)
		BASEDIR="${PWD}/$BASEDIR"
		;;
esac

LRGASP_DIR="${BASEDIR}"/lrgasp_data
TAG=1.0.0

if [ $# -gt 1 ] ; then
  input_dir="$1"
	input_gtf="$2"
  input_cage_peak="$3"
  input_polyA="$4"
  entry_json="$5"
  experiment_json="$6"
  genome_reference="$7"
  transcriptome_reference="$8"
  coverage_file="$9"
	RESDIR="${10}"



	cat <<EOF
* Using version $TAG
* Running parameters
  Input dir: $input_dir
  GTF file: $input_gtf
  CAGE peak file: $input_cage_peak
  polyA file: $input_polyA
  Json files: $entry_json / $experiment_json
  Coverage file: $coverage_file
  Results: $RESDIR
EOF


	echo "* Deriving input directory"
	inputRealPath="$(realpath "$input_dir")"
	echo $inputRealPath
	inputBasename="$(basename "$input_dir")"
	INPUTDIR="$(dirname "$inputRealPath")"
	echo $INPUTDIR
	case "$INPUTDIR" in
		/*)
			true
			;;
		*)
			INPUTDIR="${PWD}/$INPUTDIR"
			;;
	esac

	echo "* Creating $RESDIR (if it does not exist)"
	mkdir -p "$RESDIR"

	# REMEMBER: We need absolute paths for docker
	RESDIRreal="$(realpath "$RESDIR")"
	case "$RESDIRreal" in
		/*)
			true
			;;
		*)
			RESDIRreal="${PWD}/$RESDIRreal"
			;;
	esac

	ASSESSDIR="${LRGASP_DIR}"/data
	METRICS_DIR="${LRGASP_DIR}"/metrics_ref_datasets
	PUBLIC_REF_DIR="${LRGASP_DIR}"/public_ref

  echo $INPUTDIR
	echo "=> Validating input" && \
	docker run --rm -u $UID -v "${inputRealPath}":/app/input:ro -v "${RESDIRreal}":/app/output lrgasp_validation:"$TAG" \
		-c /app/input/$input_cage_peak -p /app/input/$input_polyA -e /app/input/$entry_json -x /app/input/$experiment_json && \
	echo "=> Computing metrics" && \
	docker run --rm -u $UID -v /Users/enrique/HumanCellAtlas/lrgasp_docker/lrgasp_metrics/utilities:/app/utilities:rw -v "${inputRealPath}":/app/input:rw -v "${METRICS_DIR}":/app/metrics:rw -v "${RESDIRreal}":/app/results:rw lrgasp_metrics:"$TAG" \
	   /app/input/$input_gtf /app/input/$transcriptome_reference /app/input/$genome_reference --gtf --experiment_json /app/input/$experiment_json \
	   --entry_json /app/input/$entry_json --cage_peak /app/input/$input_cage_peak --polyA_motif_list /app/input/$input_polyA \
	   -c /app/input/$coverage_file -d /app/results/results/ -o test && \
	echo "=> Assessing metrics" && \
	docker run --rm -u $UID -v "${ASSESSDIR}":/app/assess:rw -v "${RESDIRreal}":/app/results:rw lrgasp_consolidation:"$TAG" \
		-b /app/assess/ -p /app/results/assessment_dataset.json -o /app/results/ --offline OFFLINE && \
	echo "* Pipeline has finished properly"

else
	echo "Usage: $0 input_dir gtf_filename input_cage_peak input_polyA entry_json experiment_json coverage_filename results_dir"
	echo "When running, please ensure all the needed files are in the input_dir, and give filenames for the rest of the files. The output dir must also be a full path"
fi