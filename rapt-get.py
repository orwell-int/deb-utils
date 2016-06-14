import sys
import argparse

class Database(object):

    def __init__(self, file_name, url):
        self._file_name = file_name
        self._url = url
        self._memo = {}
        self._examined = set()
        self._read_lines = 0
        self._finished = False

    def load_package(self, package_name):
        if (package_name not in self._memo):
            block = []
            ignore_next_new_line = False
            read_lines = 0
            started = False
            for line in open(self._file_name, 'r'):
                read_lines += 1
                if (read_lines > self._read_lines):
                    line = line.strip('\r\n')
                    if (line.startswith('Package:')):
                        if (started):
                            package = Package(self, block)
                            self._memo[package.name] = package
                            if (package.name == package_name):
                                block = None
                                read_lines -= 1
                                break
                            else:
                                block = [line]
                        else:
                            block.append(line)
                            started = True
                    else:
                        block.append(line)
            if (block is not None):
                package = Package(self, block)
                self._memo[package.name] = package
                self._finished = True
            self._read_lines = read_lines
            if (package.name != package_name):
                package = None
                self._memo[package_name] = None
                print >>sys.stderr, "Package (" + package_name + ") not found."
        else:
            package = self._memo[package_name]
        return package

    def load_package_with_dependencies(self, package_name):
        if (package_name not in self._examined):
            package = self.load_package(package_name)
            if (package is not None):
                package.link_dependencies(self)
                self._examined.add(package.name)
                new_dependencies = package.dependencies
                while (new_dependencies):
                    dependencies = new_dependencies
                    new_dependencies = []
                    for dependency in dependencies:
                        if (dependency.name not in self._examined):
                            dependency.link_dependencies(self)
                            new_dependencies += dependency.dependencies
                            self._examined.add(dependency.name)
        else:
            package = self._memo[package_name]
        return package

    def extract_url_of_all_visited_packages(self):
        print self._url
        self._memo
        return [self._url + x.filename for x in self._memo.itervalues()]

    @property
    def url(self):
        return self._url


class Package(object):
    def __init__(self, database, block):
        self._database = database
        self._name = None
        self._filename = None
        self._direct_dependencies = []
        self._direct_dependencies_packages = []
        self.users = set()
        for line in block:
            if (line.startswith("Package:")):
                self._parse_package_line(line)
            elif (line.startswith("Depends:")):
                self._direct_dependencies = self._parse_depends_line(line)
            elif (line.startswith("Filename:")):
                self._parse_filename_line(line)

    def _parse_package_line(self, line):
        line = line[len("Package:"):]
        self._name = line.strip(' ')

    def _parse_depends_line(self, line):
        line = line[len("Depends:"):]
        raw_deps = line.split(',')
        dependencies = []
        for raw_dep in raw_deps:
            index = raw_dep.find('(')
            if (0 < index):
                raw_dep = raw_dep[:index]
            if ('|' in raw_dep):
                # not sure how to handle | in dependencies ...
                raw_dep = raw_dep.split('|')[0]
            raw_dep = raw_dep.strip(' ')
            excluded = False
            if (not excluded):
                dependencies.append(raw_dep)
        return dependencies

    def _parse_filename_line(self, line):
        line = line[len("Filename:"):]
        self._filename = line.strip(' ')

    def link_dependencies(self, database):
        for dependency in self._direct_dependencies:
            package = database.load_package(dependency)
            self._direct_dependencies_packages.append(package)
            package.users.add(self)

    @property
    def dependencies(self):
        if (self._direct_dependencies_packages is None):
            print 'Package "' + self._name + '" has no dependencies.'
        return self._direct_dependencies_packages

    @property
    def name(self):
        return self._name

    @property
    def filename(self):
        return self._filename


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        nargs='*',
        dest='packages',
        default=[],
        help='Name(s) of the package(s)')
    args = parser.parse_args()
    exclude = set()
    database = Database(
        "Packages",
        "http://ftp.debian.org/debian/",
        )
    # package = database.load_package_with_dependencies("v4l-utils")
    new_deps = []
    seen_packages_names = set()
    for package_name in args.packages:
        if (package_name in seen_packages_names):
            continue
        else:
            seen_packages_names.add(package_name)
        package = database.load_package_with_dependencies(
            package_name)
        if (package is None):
            print >>sys.stderr, "Package (" + package_name + ") not found."
            continue
        print database.url + package.filename
        new_deps.extend(package.dependencies)
    all_deps = set()
    while (new_deps):
        deps = new_deps
        new_deps = []
        for dep in deps:
            if (dep not in all_deps):
                excluded = False
                debug = False
                # if (dep.name.startswith('libx11')):
                    # debug = True
                    # print dep.name
                for exclusion in exclude:
                    if (exclusion.endswith('*')):
                        exclusion = exclusion[:-1]
                        if (debug):
                            print >>sys.stderr, "\texclusion (*):", exclusion
                        if (dep.name.startswith(exclusion)):
                            print >>sys.stderr, "Excluded (" + dep.name + \
                                ") because of '" + exclusion + \
                                "*' possibly used by: " + \
                                ", ".join([x.name for x in dep.users])
                            excluded = True
                            break
                    else:
                        if (debug):
                            print >>sys.stderr, "\texclusion:", exclusion
                        if (exclusion == dep.name):
                            print >>sys.stderr, "Excluded (" + dep.name + \
                                ") because of '" + exclusion + \
                                "' possibly used by: " + \
                                ", ".join([x.name for x in dep.users])
                            excluded = True
                            break
                if (not excluded):
                    all_deps.add(dep)
                    new_deps += dep.dependencies
    print "\n".join([database.url + x.filename for x in all_deps])

if ('__main__' == __name__):
    main()
