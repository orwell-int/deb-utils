#!/usr/bin/env zsh

# Copy a tar.gz generated with tartinator and extract.
# This is a simple script with no safety.
# $1: tarball
# $2: user to connect with (ssh passwordless)
# $3: destination machine
# $4: destination folder

main()
{
    set -e
	tarball=$1
    user=$2
    machine=$3
    folder=$4
    if [ -z "$user" ] ; then
        echo "User is missing, take root" >&2
        user=root
    fi
    if [ -z "$folder" ] ; then
        echo "Folder is missing, take \$HOME" >&2
        folder=$(ssh $user@$machine 'echo $HOME')
    fi
	if [ ! -e "$tarball" ] ; then
		echo "File '$tarball' does not exist" >&2
		exit 1
	fi
    tar_name=$(basename $tarball)
    echo scp $tarball $user@$machine:$folder/
    scp $tarball $user@$machine:$folder
    ssh $user@$machine "cd / ; tar xzf $folder/$tar_name"
}

main $*
