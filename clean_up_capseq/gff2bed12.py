#!/usr/bin/env python

import re
from collections import defaultdict

def get_gene_id(line):
    gene_id = re.search('gene_id \"([^\"]+)',line).group(1)
    transcript_id = re.search('transcript_id \"([^\"]+)',line).group(1)
    exon_number = re.search('exon_number (\d+)',line).group(1)

    return gene_id, transcript_id, exon_number

class Transcript:

    def __init__(self, gene_id, transcript_id):
        self.gene_id = gene_id
        self.transcript_id = transcript_id
        self.exon = []
        self.expression = None

    def add_expression(self, expression):
        self.expression = expression

    def add_exon(self, exon_details):
        self.exon.append(exon_details)

    def construct(self):


        exon = sorted(self.exon, key=lambda k: k['start'])

        first_exon = exon[0]

        start = first_exon['start']
        chr = first_exon['chr']
        end = exon[-1]['end']
        strand = first_exon['strand']
        block_size_field = []
        block_start_field = []
        for x in exon:
            block_size_field.append(( x['end'] - x['start'] ))
            block_start_field.append(( x['start'] - start  ))
        block_count = len(exon)

        block_size_field = [str(x) for x in block_size_field]
        block_start_field = [str(x) for x in block_start_field]

        self.bed_line  = "{chr}\t{start}\t{end}\t{transcript_id}"\
                         "\t0\t{strand}\t{start}\t{end}\t255,0,0" \
                         "\t{block_count}\t{block_sizes}\t{block_start}".format(
            chr = chr,
            start = start ,
            end = end,
            transcript_id = self.transcript_id,
            strand = strand,
            block_count = block_count,
            block_sizes = ",".join(block_size_field),
            block_start = ",".join(block_start_field)

        )

class TranscriptManager:

    def __init__(self):
        self.exon_dict = {}

    def add_exon(self, gene_id, transcript_id, exon_details):


        if self.validate_exon(exon_details):
            transcript = self.exon_dict.get(transcript_id, Transcript(gene_id, transcript_id))

            transcript.add_exon(exon_details)
            self.exon_dict[transcript_id] = transcript
            self.current_transcript = transcript

    def add_expression(self, expression):
        if self.current_transcript.expression is None:
            expression = self.__extract_expression__(expression)
            self.current_transcript.add_expression(expression)

    def __extract_expression__(self, expression):
        expression_list = expression.split(';')[3:-1]
        expression_list= [x.strip() for x in expression_list]
        expression_list = [x.split() for x in expression_list]
        expression = { k:y for (k,y) in expression_list }
        return expression

    def add_genome_size(self, data):
        self.genome_size = data

    def validate_exon(self, exon_details):
        start = exon_details['start']
        end = exon_details['end']
        chr = exon_details['chr']
        genome_size = self.genome_size[chr]
        if start > genome_size:
            exon_details = None
        elif end > genome_size:
            exon_details['end'] = genome_size

        return exon_details




def read_and_construct(filename, genome_size_file):

    genome_size = load_genome_size(genome_size_file)
    transcript_manager = TranscriptManager()
    transcript_manager.add_genome_size(genome_size)
    with open(filename) as f:
        for line in f:
            if not line.startswith('#'):
                line = line.strip()
                fields = line.split('\t')
                additional_info = fields[8]


                gene_id, transcript_id, exon_number = get_gene_id(additional_info)

                exon_details = {
                    'chr' : fields[0].replace('chr', ''),
                    'start' : int(fields[3]) + 1,
                    'end' : int(fields[4]),
                    'strand' : fields[6],
                    'exon_number' : int(exon_number)
                }


                transcript_manager.add_exon(gene_id,transcript_id ,exon_details)
                transcript_manager.add_expression(additional_info)

    return transcript_manager






def load_genome_size(genome_size_file):
    genome_dict = {}
    with open(genome_size_file) as f:
        for line in f:
            chrom , size = line.split('\t')
            genome_dict[chrom] = int(size)
    return genome_dict











