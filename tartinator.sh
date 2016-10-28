#!/usr/bin/env zsh

# Put debian packages in tar.gz files ready to be extracted in /
# This is a simple script with no safety.
# $1: destination (name of the tar.gz file with the extension).
# $2..n: debian packages to download

main()
{
	if [ -z "$TMPDIR" ] ; then
		echo "Please provide a temporary folder (TMPDIR) where files will be downloaded and extracted before being put together." >&2
		exit 1
	fi
	dest=$1
	if [ "." = "$(dirname $dest)" ] ; then
		dest=$PWD/$dest
	fi
	if [ -e $dest ] ; then
		echo "File '$dest' already exists." >&2
		exit 1
	fi
	shift
	temp_folder=$(mktemp -d)
	python rapt-get.py $* | xargs ./debinator.sh $temp_folder
	cd $temp_folder
	tar czf $dest *
}

main $*
