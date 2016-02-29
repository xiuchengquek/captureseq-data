from gff2bed12 import load_genome_size
from collections import defaultdict
from  functools import reduce
import sys


def findOverlaps(a, b):
    """

    :param a: list of exon region
    :param b: list of exon region
    :return: overlaps region and exon id
    """
    pass


def calculate_total_width(capture_file):
    """

    :param capture_file: capture file
    :return: dictionary of list , key is the chromsome and value is the total bases covered
    """

    covered_region = {}
    with open(capture_file, 'r') as f:
        for line in f:
            if not line.startswith('#') and not line.startswith('Chrom'):
                fields = line.strip().split('\t')
                chrom = fields[0].replace('chr','')
                if chrom not in covered_region:
                    covered_region[chrom] = [int(fields[3])]
                else:
                    covered_region[chrom].append(int(fields[3]))

    total_width = {}
    for key, value in covered_region.items():
        total_width[key] = 0
        for x in value:
            total_width[key] += x

    return total_width



def calculate_percentage_captured(capture_file, chrom_size):
    """

    :param capture_file: list of file with captured region
    :param region_file: file containg_chrom_size
    :return: dictionary , where key is the chromosome and the value is the percentage of region captured.
    """
    genome_size = load_genome_size(chrom_size)
    totalWidth = {}
    for x in capture_file:
       totalWidth[x] = calculate_total_width(x)

    for key, value in totalWidth.items():
        for chrom, totalbase in value.items():
            chrom_size = genome_size[chrom]
            print(totalbase / chrom_size)


def find_boundaries(capture_file):

    chrom_bound = defaultdict(list)

    with open(capture_file, 'r') as f:
        for line in f:
            if not line.startswith('#') and not line.startswith('Chrom'):
                fields = line.strip().split('\t')
                chr = fields[0].replace('chr', '')
                if chr not in chrom_bound:
                    chrom_bound[chr] = defaultdict(list)
                chrom_bound[chr]['left'].append(int(fields[1]))

                chrom_bound[chr]['right'].append(int(fields[2]))


    for chr, pair in chrom_bound.items():
        pair['left'].sort()
        left_bound=  pair['left'][0]
        pair['right'].sort(reverse=True)
        right_bound = pair['right'][0]
        chrom_bound[chr] = right_bound - left_bound


    return chrom_bound












def find_boundaries_chromosome(capture_file):

    totalWidth = {}
    boundaries = {}

    for x in capture_file :
        boundaries[x] = find_boundaries(x)

    for x in capture_file:
       totalWidth[x] = calculate_total_width(x)


    for key, value in totalWidth.items():
        for chrom, totalbase in value.items():
            chrom_size = boundaries[x][chrom]
            print(totalbase / chrom_size)



def sub_main():
    capture_files = sys.argv[1:]
    find_boundaries_chromosome(capture_files)




def main():
    genome_size_file = sys.argv[1]
    capture_files = sys.argv[2:]
    calculate_percentage_captured(capture_files, genome_size_file)



def simple_linear(capture_file, genome_size):




if __name__ == '__main__':
    sub_main()

