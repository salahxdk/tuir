#!/usr/bin/env bash

# TODO - this only links to users' emails, change this to linking to profiles
# like Michael's script

ROOT="$(dirname $0)/.."
AUTHORS="${ROOT}/AUTHORS.rst"

die() {
	echo $@
	exit 1
}

[[ -f "${AUTHORS}" ]] || die "AUTHORS.rst doesn't exist in source dir"

# Clean off the old list of contributors
sed -i '/TUIR Contributors/{n;n;Q}' ${AUTHORS}

# Add new ones
# Get a list of the "Author" fields from the commits since I took over
# maintainence of TUIR, dedupe those and format for the AUTHORS.rst file
CONTRIBUTORS=$(git log v1.27.0..HEAD |
	awk '$1 ~ /Author:/' |
	awk '!a[$0]++' |
	sed 's/Author: /* `/; s/$/`_/g')
# TODO - Surely there's a way to compress these awks and sed into a single
# command...

# Add a space between the heading and contributors
echo "" >> ${AUTHORS}
echo "${CONTRIBUTORS}" >> ${AUTHORS}
