#!/bin/bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

set -x
set -e

# Extra package source for moviepy stuff
echo deb http://www.deb-multimedia.org stretch main non-free >> /etc/apt/sources.list
echo deb-src http://www.deb-multimedia.org stretch main non-free >> /etc/apt/sources.list

apt-get update

cat ${BASEDIR}/packages-imageopt.txt | sed '/^#/ d' | sed '/^$/d' | xargs apt-get install -y --force-yes --no-install-recommends
cat ${BASEDIR}/packages-moviepy.txt | sed '/^#/ d' | sed '/^$/d' | xargs apt-get install -y --force-yes --no-install-recommends

# cleanup
rm -rf /var/lib/apt/lists/*
apt-get clean
