





import re
from collections import defaultdict

import json


def load_json_file(json_file, fh_out):
    fh_in = open(json_file,  'r' )
    expression_json = json.load(fh_in)
    entries = list(expression_json.keys())
    initial_data = []

    modeltype = ''
    if entries[0].startswith('GC'):
        modeltype = 'capseq.TissueExpression'
    elif entries[0].startswith('TCON'):
        modeltype = 'capseq.MelanomaExpression'

    pk = 1
    for key, value in expression_json.items():
        if modeltype == 'capseq.TissueExpression':
            entry =  {'model' : modeltype ,
             'pk' : pk,
             'fields': {
                 'transcript_id' : key,
                  'expression' :  value

             }}
        elif modeltype == 'capseq.MelanomaExpression':


            del value['class_code']
            del value['oId']
            del value['tss_id']

            try :
                gene_name = value['gene_name']
                del value['gene_name']
                del value['nearest_ref']
                del value['p_id']

            except KeyError :
                gene_name = key


            value = {k:float(v) for k,v in  value.items()}
            entry =  {'model' : modeltype ,
             'pk' : pk,
             'fields': {
                 'transcript_id' : key,
                 'gene_name' : str(gene_name),
                  'expression' :  value

             }}
        initial_data.append(entry)
        pk += 1

    with open(fh_out, 'w') as f:
        json.dump(initial_data,f )

    fh_in.close()



def load_exon_json(json_file_list, fh_out):
    initial_data = []

    for json_file in json_file_list:

        fh_in = open(json_file,  'r' )
        transcript_json = json.load(fh_in)
        pk = 1

        for key, value in transcript_json.items():
            entry =  {'model' : 'capseq.TranscriptInfo' ,
                 'pk' : pk,
                 'fields': {
                     'transcript_id' : key,
                      'exons' :  value

                 }}
            initial_data.append(entry)
            pk += 1


        fh_in.close()
    with open(fh_out, 'w') as f:
        json.dump(initial_data, f)




class CaptureRegions:
    def __init__(self, disease, snps):
        self.disease = disease.split(';')
        self.snps = snps.split(';')
        self.snps_pubmed = defaultdict(list)

    def find_pubmed(self):
        snps = self.snps
        disease = self.disease
        for x in snps:

            snp_id, pvalue= re.split('\s+', x)
            pvalue = pvalue.replace('(', '')
            pvalue = pvalue.replace(')', '')
            pvalue , pubmed = pvalue.split(',')


            self.snps_pubmed["snps"].append(
                {
                    "snp_id" : str(snp_id),
                    "pvalue" : str(pvalue),
                    "pubmed" : int(pubmed),
                }
            )

        self.snps_pubmed["disease"] = disease












def generate_json_file(input_list, fh_out):
    initial_data = []
    pk = 1

    for input_file in input_list:
        track = 'tissue'
        if 'melanoma' in input_file:
            track = 'melanoma'

        fh_in = open(input_file,  'r' )
        for line in fh_in:
            if not line.startswith('Chromo'):
                fields = line.strip().split('\t')
                chr, start, end, width, name = fields[:5]

                if track == 'melanoma':
                    details = {'snps' : [{
                            'snp_id' : fields[4]}],
                            'disease' : [fields[5]]}


                else :
                    disease, snps = fields[6:]
                    region = CaptureRegions(disease, snps)
                    region.find_pubmed()
                    details = region.snps_pubmed



                entry =  {'model' : 'capseq.CapturedRegion' ,
                     'pk' : pk,
                     'fields': {
                         'chr' : chr.replace('chr', ''),
                          'start' :  int(start),
                          'end' :  int(end),
                          'width' : int(width),
                          'name' : str(name),
                          'track' : track,
                          'details' : details
                        }}
                initial_data.append(entry)
                pk += 1
        fh_in.close()
    with open(fh_out, 'w') as f:
        json.dump(initial_data, f)








