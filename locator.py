#!/usr/bin/env python3

import sys
import os
import gzip
import zlib
import argparse


HEXDICT = {
    "S": "24",
    "M": "48",
    "L": "6C",
    "XL": "90",
    "H": "B4",
    "EH": "D8",
    "G": "FC"
}


class Locator:
    def __init__(self, params):
        self.mappath = params.mapdir
        self.mapsizes = [x.strip().lower() for x in params.size.split(',')]
        self.check_hex()
        self.respath = params.outputdir

    def check_hex(self):
        d = [x.lower() for x in HEXDICT]
        for key in self.mapsizes:
            if key not in d:
                exit_error("Incorrect map size: {}".format(key))

    def walker(self):
        dir_made = False
        with os.scandir(self.mappath) as path:
            for element in path:
                if element.is_file():
                    file = self.unzip(element.path)
                    if file:
                        found = self.parse(file)
                        if found:
                            if not dir_made:
                                self.makedir()
                                dir_made = True
                            self.move(element.name)

    def makedir(self):
        if not os.path.exists(self.respath):
            try:
                os.mkdir(self.respath)
            except Exception:
                exit_error("Cannot create output directory.")

    def unzip(self, filename):
        try:
            f = gzip.open(filename, "r")
        except Exception:
            return False
        else:
            return f

    def parse(self, file):
        try:
            data = file.read(30)
        except (OSError, zlib.error):
            return False
        else:
            for index, byte in enumerate(data, start=1):
                if hex(byte).split('x')[1] == '1':
                    break
            else:
                index = False
            # print(file.name, "\nIndex:", index, "\nData:", data, "\n")
            try:
                res = hex(data[index]).split('x')[1]
            except IndexError:
                return False
            if index:
                for size in self.mapsizes:
                    if res == HEXDICT[size.upper()].lower():
                        return True
            else:
                return False
        finally:
            file.close()

    def move(self, filename):
        outpath = os.path.join(self.respath, filename)
        if not os.path.exists(outpath):
            try:
                os.rename(os.path.join(self.mappath, filename), outpath)
            except Exception:
                print("Cannot move file {}.".format(filename))
        else:
            print("Cannot move file {}: it already exists in target directory.".format(filename))


def parse_arguments():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--size", help="Map size: comma-separated list of S, M, L, XL, H, XH, G.")
    parser.add_argument("-m", "--mapdir", help="Directory where to locate maps.", required=True)
    parser.add_argument("-o", "--outputdir", help="Directory where to store found maps.", required=True)
    return parser.parse_args()


def exit_error(message):
    sys.exit(message)


if __name__ == "__main__":
    args = parse_arguments()
    locator = Locator(args)
    locator.walker()