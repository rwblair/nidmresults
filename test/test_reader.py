#!/usr/bin/env python
"""
Test NIDM FSL export tool installation


@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>
@copyright: University of Warwick 2013-2015
"""
import unittest
from nidmresults.graph import *
from nidmresults.test.test_results_doc import TestResultDataModel
from future.standard_library import hooks
# with hooks():
#     from urllib.request import urlopen, Request

from nidmresults.owl.owl_reader import OwlReader

import zipfile
import json
# from ddt import ddt, data, unpack
import os
import inspect
import glob
import shutil
from rdflib.compare import isomorphic, graph_diff

import os


# @ddt
class TestReader(unittest.TestCase, TestResultDataModel):

    def setUp(self):
        self.my_execption = ""
        
        owl_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'nidmresults', 'owl', 'nidm-results_130.owl')
        self.owl = OwlReader(owl_file)

        pwd = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe())))

        # Store test data in a 'data' folder until 'test'
        data_dir = os.path.join(pwd, 'data')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # # Collection containing examples of NIDM-Results packs (1.3.0)
        # req = Request(
        #     "http://neurovault.org/api/collections/2210/nidm_results")
        # rep = urlopen(req)

        # response = rep.read()
        # data = json.loads(response.decode('utf-8'))

        # # Download the NIDM-Results packs from NeuroVault if not available
        # # locally
        # self.packs = list()
        # for nidm_res in data["results"]:
        #     url = nidm_res["zip_file"]
        #     study = nidm_res["name"]

        #     nidmpack = os.path.join(data_dir, study + ".zip")
        #     if not os.path.isfile(nidmpack):
        #         f = urlopen(url)
        #         print("downloading " + url + " at " + nidmpack)
        #         with open(nidmpack, "wb") as local_file:
        #             local_file.write(f.read())
        #     self.packs.append(nidmpack)

        self.packs = glob.glob(os.path.join(data_dir, '*.nidm.zip'))
        self.out_dir = os.path.join(data_dir, 'recomputed')

        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)

        os.mkdir(self.out_dir)

    # @unpack
    # @data({'name': 'excursion set', 'method_name': 'get_excursion_set_maps'},
    #       {'name': 'statistic map', 'method_name': 'get_statistic_maps'})
    def test_read_object(self):
        """
        Test: Check that excursion set can be retreived
        """
        exc = []
        for nidmpack in self.packs:
            print(nidmpack)

            # This is a workaround to avoid confusion between attribute and class uncorrected p-value
            # cf. https://github.com/incf-nidash/nidm/issues/421
            to_replace = {'@prefix nidm_PValueUncorrected: <http://purl.org/nidash/nidm#NIDM_0000160>': 
                          '@prefix nidm_UncorrectedPValue: <http://purl.org/nidash/nidm#NIDM_0000160>',
                          'nidm_PValueUncorrected': 'nidm_UncorrectedPValue',
                          'nidm_PValueUncorrected': 'nidm_UncorrectedPValue',
                          'http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/': 
                          'http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions#'}

            nidmres = NIDMResults(nidm_zip=nidmpack, to_replace=to_replace)
            new_name = os.path.join(self.out_dir, os.path.basename(nidmpack))
            nidmres.serialize(new_name)
            print('Serialised to ' + new_name)
            print("----")

            new_nidmres = NIDMResults(nidm_zip=new_name)

            self.compare_full_graphs(nidmres.graph, new_nidmres.graph, self.owl, True, True, reconcile=False)

            # nidm_graph.parse()
            # # exc_sets = nidm_graph.get_excursion_set_maps()

            # method = getattr(nidm_graph, method_name)
            # objects = method()

            # if not objects:
            #     exc.append('No ' + name + ' found for ' + nidmpack)

            # for eid, eobj in objects.items():
            #     with zipfile.ZipFile(nidmpack, 'r') as myzip:
            #         if not str(eobj.file.path) in myzip.namelist():
            #             exc.append(
            #                 'Missing ' + name + ' file for ' + nidmpack)

        # if exc:
        #     raise Exception("\n ".join(exc))

if __name__ == '__main__':
    unittest.main()
