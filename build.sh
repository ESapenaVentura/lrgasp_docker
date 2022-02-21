#!/bin/bash

type -a docker > /dev/null

if [ $? -ne 0 ] ; then
	echo "UNCONFIGURED: No docker executable" 1>&2
	exit 1
fi

set -e
if [ $# -gt 0 ]; then
	tag_id="$1"

	for docker_name in lrgasp_validation ; do
		echo "Building ${docker_name}:${tag_id}"
		docker build -t "$docker_name":"$tag_id" "$docker_name"
	done
else
	echo "Usage: $0 tag_id" 1>&2
	exit 1
fi