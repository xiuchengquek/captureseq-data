#!/usr/bin/env python




import unittest
from .gff2bed12 import Transcript, TranscriptManager




class TranscriptTestCase(unittest.TestCase):


    def setUp(self):
        self.mock_gene_id = 'GeneA'
        self.mock_transcript_id = 'TranscriptA'
        self.mock_exon_1 = {
            'chr' : "1",
            'start' : 10,
            'end' : 100,
            'strand' : "-"
        }
        self.mock_exon_2 = {
            'chr' : "1",
            'start' : 120,
            'end' : 150,
            'strand' : "-"
        }


    def test_add_exon(self):
        transcriptA = Transcript(self.mock_gene_id, self.mock_transcript_id )
        transcriptA.add_exon((self.mock_exon_1))
        transcriptA.add_exon((self.mock_exon_2))
        transcriptA.construct()

        self.assertEqual(transcriptA.gene_id, 'GeneA', 'Trnascript Intilization is correct')
        self.assertEqual(transcriptA.transcript_id, 'TranscriptA', 'Trnascript Intilization is correct')
        self.assertDictEqual(transcriptA.exon[0], self.mock_exon_1, msg='exon added' )
        self.assertDictEqual(transcriptA.exon[1], self.mock_exon_2, msg='exon added' )
        self.assertEqual(transcriptA.bed_line, '1\t10\t150\tTranscriptA\t0\t-\t10\t150\t255,0,0\t2\t91,31\t0,110')







class TranscriptManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.gene_a = 'gene_a'
        self.transcript_a = 'transcript_a'

        self.gene_a_exons = [
            {   'chr' : "1",
                'start' : 10,
                'end' : 100,
                'strand' : "-"
            },
            {
                'chr' : "1",
                'start' : 120,
                'end' : 150,
                'strand' : "-"
            }
        ]

        self.gene_b = 'gene_a'
        self.transcript_b = 'transcript_b'
        self.gene_b_exons = [
            {   'chr' : "2",
                'start' : 10,
                'end' : 100,
                'strand' : "-"
            },
            {
                'chr' : "2",
                'start' : 120,
                'end' : 150,
                'strand' : "-"
            }
        ]

        self.mock_genome = {
            "1" : 100000,
            "2" : 200000
        }

        self.gene_b_large_exons = {
            'chr' : "2",
            'start' : 50000000,
            'end' :  60000000
        }


        self.gene_b_large_end = {
            'chr' : "2",
            'start' : 300,
            'end' :  300000
        }

        self.transcript_manager = TranscriptManager()

    def test_manager_add_exon(self):
        self.transcript_manager.add_genome_size(self.mock_genome)

        self.transcript_manager.add_exon(self.gene_a, self.transcript_a, self.gene_a_exons[0])
        self.assertEqual(self.transcript_manager.current_transcript.transcript_id, 'transcript_a')

        self.transcript_manager.add_exon(self.gene_a, self.transcript_a, self.gene_a_exons[1])
        self.transcript_manager.add_exon(self.gene_b, self.transcript_b, self.gene_b_exons[0])

        self.assertEqual(self.transcript_manager.current_transcript.transcript_id, 'transcript_b')

        self.transcript_manager.add_exon(self.gene_b, self.transcript_b, self.gene_b_exons[1])
        transcript_a = self.transcript_manager.exon_dict['transcript_a']
        self.assertEqual(transcript_a.gene_id , 'gene_a')
        self.assertEqual(transcript_a.transcript_id , 'transcript_a')
        transcript_b = self.transcript_manager.exon_dict['transcript_b']
        self.assertEqual(transcript_b.gene_id , 'gene_a')
        self.assertEqual(transcript_b.transcript_id , 'transcript_b')

        self.assertListEqual(transcript_b.exon,  self.gene_b_exons)
        self.assertListEqual(transcript_a.exon,  self.gene_a_exons)


    def test_manager_genome(self):
        self.transcript_manager.add_genome_size(self.mock_genome)

        self.assertIsNone(self.transcript_manager.validate_exon(self.gene_b_large_exons))

        trimmed_exon = {
            'chr' : "2",
            'start' : 300,
            'end' :  200000
        }
        self.assertDictEqual(trimmed_exon, self.transcript_manager.validate_exon(self.gene_b_large_end))
        self.assertDictEqual(self.gene_b_exons[0], self.transcript_manager.validate_exon( self.gene_b_exons[0]))





























