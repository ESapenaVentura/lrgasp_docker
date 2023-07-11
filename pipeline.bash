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
  input_file="$1"
	RESDIR="$3"
	TAG="$2"
	challenges="$4"
	if [ $# -gt 4 ] ; then
	  for i in $(seq 5 $#); do
	    eval "arg=\${$i}"
	    challenges+=" $arg"
	  done
	fi




	cat <<EOF
* Using version $TAG
* Running parameters
  Input file: $input_file
  Results: $RESDIR
  Tag: $TAG
  Challenges: $challenges
EOF


	echo "* Deriving input directory"
	inputRealPath="$(realpath "$input_file")"
	echo $inputRealPath
	inputBasename="$(basename "$input_file")"
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

	echo "=> Validating input" && \
	docker run --rm -u $UID -v "${INPUTDIR}":/app/input:rw -v "${RESDIRreal}":/app/output:rw lrgasp_validation:"$TAG" \
		 -i /app/input/$inputBasename -o /app/output/participant.json --challenges "$challenges" -m && \

	echo "=> Computing metrics" && \
	docker run --rm -u $UID -v /Users/enrique/HumanCellAtlas/lrgasp_docker/lrgasp_metrics/utilities:/app/utilities:rw -v "${INPUTDIR}":/app/input:rw -v "${METRICS_DIR}":/app/metrics:rw -v "${RESDIRreal}":/app/output:rw lrgasp_metrics:"$TAG" \
	   --input-gz-file /app/input/$inputBasename --manifest --ref-directory /app/input/public_ref --gtf -d /app/output/results/ -o results --assesment-output /app/output/assessment.json --challenges "$challenges" && \

	echo "=> Assessing metrics" && \
	docker run --rm -u $UID -v "${ASSESSDIR}":/app/assess:rw -v "${RESDIRreal}":/app/output:rw lrgasp_consolidation:"$TAG" \
		-b /app/assess/ -p /app/output/assessment.json -o /app/output/ --offline OFFLINE && \
	echo "* Pipeline has finished properly"

else
	echo "Usage: $0 input_file TAG results_dir challenges"
	echo "When running, please ensure all the needed files are in the input_file, included the manifest with the filenames. The output dir must also be a full path"
fi