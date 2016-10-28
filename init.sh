# Download the Packages file used to know about the different packages.
# You may want to download a recent version, possibly by removing the
# one you have.
# This is mostly an example and fits some needs. A file for a different
# debian distribution should work too.
# This is needed by rapt-get.pp

if [ ! -e Pacakges ] ; then
	wget http://ftp.debian.org/debian/dists/jessie/main/binary-armel/Packages.xz
	xz -d Packages.xz 
fi
