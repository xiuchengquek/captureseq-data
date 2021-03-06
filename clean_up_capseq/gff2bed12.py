#!/usr/bin/env python

import re
from collections import defaultdict
import json
import copy

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


        for i,x in enumerate(exon):
            x['exon_number'] = i

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



    def validate_transcript(self, error_file):


        exon = sorted(self.exon, key=lambda k: (k['start'], k['end']))
        validated_exons = []
        prev = {}

        for i,x in enumerate(exon):
            if i == 0:
                prev = copy.deepcopy(exon[i])
            else :
                case = (0,0,0)

                ## current exon is within previous exon
                if (prev['end'] >= x['end']) and (prev['start'] >= x['start']):
                    error_file.write("%s\n" % self.transcript_id)
                #elif  (prev['end'] >= x['start']) and (prev['end'] <= x['end']) and (prev['end'] <= x['start'] ):
                elif  ( prev['end'] >= x['start']) and (prev['end'] <= x['end'] ):
                    prev['end'] = x['end']

                    error_file.write("%s\n" % self.transcript_id)
                elif  ( prev['start'] >= x['start']) and (prev['end'] <= x['end'] ):
                    pass
                elif (prev['start'] <= x['start'])and (prev['end'] >= x['start']):
                    pass


                else:

                    validated_exons.append(x)

                    prev = x


        ## if len validated is 0 append th
        if len(validated_exons) > 0:
            self.exon = validated_exons
        else :
            self.exon = [exon[0]]






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
                    'start' : int(fields[3]) ,
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


def simple_gtf_bed(file, outbed,expression_json):

    fh_out = open(outbed, 'w')
    json_out = open(expression_json, 'w')
    json_expression  = {}


    with open(file, 'r') as f:
        for line in f :
            if not line.startswith('#'):
                line = line.strip()
                fields =  line.split('\t')
                gene_id, transcript_id, exon_number = get_gene_id(fields[8])
                chr = fields[0].replace('chr','')

                bed_line = "{chr}\t{start}\t{end}\t{transcript_id}-{exon_number}\t0\t{strand}\n".format(
                    chr = chr,
                    start = fields[3],
                    end = fields[4],
                    transcript_id = transcript_id,
                    exon_number = exon_number,
                    strand = fields[6]
                )

                fh_out.write(bed_line)

                expression_list = fields[8].split(';')[3:-1]
                expression_list= [x.strip() for x in expression_list]
                expression_list = [x.split() for x in expression_list]
                expression = { k:y for (k,y) in expression_list }
                json_expression[transcript_id] = expression


    json.dump(json_expression, json_out)
    json_out.close()
    fh_out.close()


def generate_auto_sql(outfile):
    as_out =  """table tissue_cap_ex
"Capseq table with expression data of body altas"(
string chrom; "Reference sequence chromosome or scaffold"
uint chromStart; "Start position of feature on chromosome"
uint chromEnd; "End position of feature on chromosome"
string name; "Name of gene"
uint score; "Score"
char[1] strand; "+ or - for strand"
float[6] adipose; "adipose expression"
float[6] bladder; "bladder expression"
float[6] brain; "brain expression"
float[6] breast; "breast expression"
float[6] cervix; "cervix expression"
float[6] colon; "colon expression"
float[6] esophagus; "esophagus expression"
float[6] heart; "heart expression"
float[6] kidney; "kidney expression"
float[6] liver; "liver expression"
float[6] lung; "lung expression"
float[6] ovary; "ovary expression"
float[6] placenta; "placenta expression"
float[6] prostate; "prostate expression"
float[6] skmusc; "skmusc expression"
float[6] smint; "smint expression"
float[6] spleen; "spleen expression"
float[6] testes; "testes expression"
float[6] thymus; "thymus expression"
float[6] thyroid; "thyroid expression"
float[6] trachea; "trachea expression"
)
    """
    with open(outfile, 'w') as f :
        f.write("%s\n" %as_out)


def join_expression(bed_file, expression_file, output, as_file):




    with open(expression_file, 'r') as f :
        expression = json.load(f)
    expression_order = ["adipose", "bladder", "brain", "breast",
                        "cervix", "colon", "esophagus", "heart",
                        "kidney", "liver", "lung", "ovary", "placenta",
                        "prostate", "skmusc", "smint", "spleen", "testes",
                        "thymus", "thyroid", "trachea"]

    fh_out = open(output, 'w')

    with open(bed_file) as f:
        for line in f:
            line = line.strip()
            fields = line.split('\t')
            transcript = fields[3]

            expression_line = expression[transcript]
            expression_line = [str(expression_line[x]) for x in expression_order]
            fields.extend(expression_line)
            outline = "\t".join(fields)
            fh_out.write("%s\n" % outline)

    fh_out.close()
    generate_auto_sql(as_file)








