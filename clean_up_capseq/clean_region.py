#!/usr/bin/python

import re
import subprocess
import os
from nltk.corpus import stopwords
cwd = os.path.dirname(os.path.realpath(__file__))

print(cwd)


def clean_line(line):
    """

    :param line: input line for capture region file
    :return: list containing output
    """
    line = re.sub("^chr", "", line)
    fields = line.split('\t')
    snps = fields[4].split(';')
    results = []
    for x in snps:
        results.append(
            "{chr}\t{start}\t{end}\t{snpid}".format(chr=fields[0],
                                                start=fields[1],
                                                end=fields[2],
                                                snpid = x)
                       )

    return results


def generate_trix(line):
    line = re.sub("^chr", "", line)
    fields = line.split('\t')
    snps = fields[4].split(';')
    keywords = re.findall(r"[\w']+", fields[5])
    keywords = [y.lower() for y in keywords ]
    keywords = [ y for y in keywords if y not in stopwords ]
    results = []

    for x in snps:
        pass









def write_output(results, fh_out):
    """

    :param results: list contain lines to write out
    :param fh_out: fh handle of out fle
    :return: None
    """
    for line in results:
        fh_out.write("%s\n" % line)

def clean_region(file, outfile):
    fh_out = open(outfile, 'w')
    with open(file, 'r') as f:
        for line in f:
            if not line.startswith('Chromosome'):
                results = clean_line(line)
                write_output(results, fh_out)




def convert_to_binary(input, output, bedformat, index=True, chrom_size_file=os.path.join(cwd, 'data/hg19.chrom.sizes.nochr')):
    bedtoBigBed= os.path.join(cwd, 'bedToBigBed')

    cmd = [bedtoBigBed , '-tab', input, chrom_size_file, output]
    if index is True:
        cmd.insert(1, '-type=' + bedformat)
        cmd.insert(1, '-extraIndex=name')
    subprocess.check_call(cmd)




