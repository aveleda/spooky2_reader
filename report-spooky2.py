#!/usr/bin/python3
#
# Copyright 2022 Albino Aveleda <albino@bino.eng.br>
# summary report spooky2
#
import argparse

def main():
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-i", "--input", help="input file", required=True)
    parser.add_argument("-o", "--output", help="output file", required=False)

    # Read arguments from command line
    args = parser.parse_args()

    if args.input:
        filename = args.input
    if args.output:
        fileout = args.output
    else:
        fileout = filename[:-3] + "csv"
    lines = readfile(filename)
    result = createDict(lines)
    printCsv(result, fileout)


def readfile(filename):
    with open(filename) as f:
        lines = (line.rstrip() for line in f)
        lines = (line for line in lines if line)
        lines = list(line for line in lines if line[:3] != "BFB")
    # remove header
    line = lines[0]
    while line[:5] != "-----":
        lines.pop(0)
        line = lines[0]
    lines.pop(0)
    return lines


def createDict(lines):
    matches = {}
    for line in lines:
        indice = line.rfind("(")
        if (indice > 0) and (line.rfind("(SD)") == -1) and (line.rfind("(MW)") == -1):
            if line.rfind("Hz") > 0:
                line = line[:indice-1]
            previous_count = matches.get(line, 0)
            matches[line] = previous_count + 1
    return matches


def printCsv(varDict, filename):
    with open(filename, 'w') as f:
        for key, value in sorted(varDict.items()):
            ind = key.rfind("(")
            database = key[ind + 1:-1]
            line = key[:ind - 1]
            f.writelines(line + "," + str(value) + "," + database + "\n")


if __name__ == '__main__':
    main()
