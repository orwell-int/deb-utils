#!/usr/bin/env zsh

# Download, extract and fake install debian files.
# This is a simple script with no safety.
# $1: destination (like PREFIX).
# $2..n: debian files to download and fake install in $1 (complete urls are needed).

download()
{
	archive=${1##*/}
	if [ ! -e "$archive" ] ; then
		wget -N -q $1
	fi
}

extract()
{
	archive=${1##*/}
	dest=$2
	folder=${archive%.deb}
	dir=$PWD
	if [ ! -e "$folder" ] ; then
		mkdir "$folder"
		cd "$folder"
		ar vx ../$archive
		if [ -e "data.tar.xz" ] ; then
			xz -d data.tar.xz
			is_gz=
		else
			is_gz=1
		fi
	else
		cd $folder
		if [ -e "data.tar" ] ; then
			is_gz=
		else
			is_gz=1
		fi
	fi
	sub_folder=$PWD
	cd $dest
	if [ -z "$is_gz" ] ; then
		tar xf "$sub_folder/data.tar"
	else
		tar xzf "$sub_folder/data.tar.gz"
	fi
	echo "Files extracted for '$1'." >&2
	#else
	#	echo "Nothing extracted for '$1' because '$dir/$folder' already exists." >&2
	#fi
}

main()
{
	if [ -z "$TMPDIR" ] ; then
		echo "Please provide a temporary folder (TMPDIR) where files will be downloaded and extracted before being put together." >&2
		exit 1
	fi
	dest=$1
	shift
	while [ $# -gt 0 ] ; do
		cd $TMPDIR
		mkdir -p debinator
		cd debinator
		download $1
		extract $1 $dest
		shift
	done
}

main $*
