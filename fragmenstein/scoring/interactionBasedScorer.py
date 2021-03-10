#!/usr/bin/env python

"""
Scoring based on interactions preservation
"""
import os
import dask
import re
import numpy as np
from itertools import chain

from rdkit.Chem.Descriptors import ExactMolWt

from fragmenstein.external.plip.PlipWrapper import PlipWrapper
from fragmenstein.scoring._scorer_base import _ScorerBase, journal
from fragmenstein.utils.io_utils import apply_func_to_files


class InteractionBasedScorer(_ScorerBase):

    MIN_NUM_CONTACTS_FOR_POSITIVE_FRAGMENT = 2
    MIN_NUM_CONTACTS_FOR_POSITIVE_MATCH = 2

    #TODO: add weight by interaction type Typical Energies Salt Bridge ~2 kcal/mol H-Bond ~1 kcal/mol Hydrophobic ~0.7 kcal/mol Aromatic ~1-3 kcal/mol

    def __init__(self, fragments_dir, fragment_id_pattern, boundPdbs_to_score_dir, boundPdbs_to_score_pattern,
                 fragment_match_threshold=0.5, selected_fragment_ids=None,
                 ligand_resname="LIG", *args, **kwargs):
        '''
        This params are generally provided through the class method computeScoreForMolecules
        args/kwargs must contain working_directory

        '''

        self.selected_fragment_ids = selected_fragment_ids
        self.fragment_match_threshold= fragment_match_threshold
        self.fragment_id_pattern = fragment_id_pattern
        self.boundPdbs_to_score_dir = boundPdbs_to_score_dir
        self.boundPdbs_to_score_pattern = boundPdbs_to_score_pattern
        self.ligand_resname = ligand_resname
        self.fragments_dir = fragments_dir
        self.plipWorker = PlipWrapper()

        super().__init__( *args, **kwargs)

        journal.warning("Computing interactions for fragments")



        self._fragInteractions_dict = None

        journal.warning("Fragments interactions computed")

        def prepare_bound_pdbNames(fname):
            return ((re.match(self.boundPdbs_to_score_pattern,  os.path.basename(fname)).group(1),
              os.path.join(self.boundPdbs_to_score_dir, fname)))

        self.atomic_models_fnames = dict(apply_func_to_files(self.boundPdbs_to_score_dir, self.boundPdbs_to_score_pattern,
                                                                  prepare_bound_pdbNames))


    @property
    def fragInteractions_dict(self):
        if not self._fragInteractions_dict:
            def load_fragments_interactions(bound_pdb_fname):
                return self._computeInteractionsOneComplex(bound_pdb_fname, selected_fragment_ids=self.selected_fragment_ids)
            self._fragInteractions_dict = dict(filter(None.__ne__,
                                                     apply_func_to_files(self.fragments_dir, self.fragment_id_pattern,
                                                                         load_fragments_interactions)))
        return self._fragInteractions_dict

    @property
    def fragments_id(self):
        '''
        This is instantiation of abstract attribute
        :return: the list of all fragment ids that have been loaded
        '''
        return list( self.fragInteractions_dict.keys() )

    def _computeInteractionsOneComplex(self, bound_pdb_fname, pattern= None, selected_fragment_ids=None):
        '''
        :param bound_pdb_fname:
        :return:
        '''
        # re.match is ensured if  bound_pdb_fname comes  from self.atomic_models_fnames or self.fragInteractionsDicts
        assert  bound_pdb_fname.endswith(".pdb"), "Error, framgent_dir and fragment_ids should point to bound pdb files"
        if not pattern:
            pattern= self.fragment_id_pattern
        frag_id = re.match(pattern, os.path.basename(bound_pdb_fname)).group(1)
        if selected_fragment_ids and frag_id not in selected_fragment_ids:
            return None

        inters = self.plipWorker.compute_interactions_boundPDB(bound_pdb_fname)
        inters = set (chain.from_iterable( ( (inter_type.replace("_","-")+"_"+res_id for res_id in res_list)  for inter_type, res_list in inters.items() ) ) )
        return (frag_id, inters)


    def computeScoreOneMolecule(self, mol_id, mol, frag_ids, *args, **kwargs):
        '''
        :param mol_id: an id of the molecule.
        :param mol: a molecule to evaluate
        :param frag_ids: a list of fragment ids
        :return:
        '''
        try:
            pdb_fname = self.atomic_models_fnames[mol_id]

            current_frag_id, mol_inter_residues = self._computeInteractionsOneComplex(pdb_fname,
                                                                                      pattern=self.boundPdbs_to_score_pattern)

            selected_frag_ids = []
            per_fragment_score = []
            already_shared_interactions = set([])
            all_fragments_interactions = set([])
            for frag_id in frag_ids:
                frag_inter_residues = self.fragInteractions_dict.get(frag_id, None)
                if frag_inter_residues is None or len(
                    frag_inter_residues) < InteractionBasedScorer.MIN_NUM_CONTACTS_FOR_POSITIVE_FRAGMENT:
                    continue
                else:

                    all_fragments_interactions = all_fragments_interactions.union(frag_inter_residues)

                    shared = mol_inter_residues & frag_inter_residues
                    # novel = mol_inter_residues - frag_inter_residues
                    # lost = frag_inter_residues - mol_inter_residues

                    n_shared = len(shared)
                    if n_shared > InteractionBasedScorer.MIN_NUM_CONTACTS_FOR_POSITIVE_MATCH:
                        per_fragment_conservation = n_shared / float(
                            len(frag_inter_residues))  # TODO: avoid computing len for each molecule
                        selected_frag_ids.append(frag_id)
                        per_fragment_score.append(per_fragment_conservation)

                        already_shared_interactions = already_shared_interactions.union(shared)
                    else:
                        # TODO: Add penalty
                        pass

            selected_fragments = [(f_id, score) for f_id, score in zip(selected_frag_ids, per_fragment_score)
                                  if score > self.fragment_match_threshold]

            gobal_score = (1 + len(already_shared_interactions)) / (1 + float(len(all_fragments_interactions)))
            if len(selected_fragments) > 0:
                fragments, per_fragment_score = zip(*selected_fragments)
                score_interPreservPerFrag = np.median(per_fragment_score)
            else:
                score_interPreservPerFrag = 0
                fragments = []
        except KeyError:
            journal.warning("Warning, not pdb file found for the mol_id: %s"%mol_id)
            score_interPreservPerFrag= np.nan
            gobal_score = np.nan
            fragments = []
        partial_results = {_ScorerBase.MOL_NAME_ID: mol_id,
                           _ScorerBase.SCORE_NAME_TEMPLATE % "plipMedianPreser": score_interPreservPerFrag,
                           _ScorerBase.SCORE_NAME_TEMPLATE % "plipGlobalPreser": gobal_score,
                           _ScorerBase.SCORE_NAME_TEMPLATE % "plipGlobalPreserOverMw": 100. * gobal_score / ExactMolWt(mol),
                           _ScorerBase.FRAGMENTS_ID: list(fragments)}
        return partial_results

    @classmethod
    def parseCmd(cls):
        description = "Interactions preservation scoring with plip"
        additional_args = [

                            ('-f', '--fragments_dir', dict(required=True, type=str, help='Directory with a PDB file for each BOUND pdb-fragment. '
                                                                                          'PDB format required. Fragments can also be located in subdirectories)')),
                            ('-p', '--fragment_id_pattern', dict(required=False, help='Regex pattern for the BOUND pdb files.', default="(.+)_bound\.pdb$")),

                            ('-a', '--boundPdbs_to_score_dir', dict(type=str, required=True,
                                                                   help='Directory with a PDB file for each BOUND pdb-compound to evaluate. '
                                                                        'PDB format required. Fragments can also be located in subdirectories)')),
                            ('--boundPdbs_to_score_pattern', dict(type=str, required=False, default = ".*-(\w+)_bound\.pdb$",
                                                               help='Pattern for the BOUND pdb associated to compounds file name')),
                            ('--ligand_resname', dict(type=str, required=False, default="LIG",
                                                           help='Directory where atomic models for bound structures are located')),

                           ]
        return _ScorerBase.parseCmd(description, additional_args)


if __name__ == "__main__":

    results = InteractionBasedScorer.evalPipeline(initiaze_parallel_execution=True)
    print(results)

'''
python -m fragmenstein.scoring.interactionBasedScorer -i /home/ruben/oxford/myProjects/diamondCovid/data/Mpro/compound_vs_fragments.csv -d /home/ruben/oxford/myProjects/diamondCovid/data/Mpro/aligned -f /home/ruben/oxford/myProjects/diamondCovid/data/Mpro/aligned  -o compound-set_interactPreserv.csv -s  compound-setinteractPreserv.sdf -p ".*-(\w+)_bound.pdb$" -w ~/tmp/test_dask -a /home/ruben/oxford/myProjects/diamondCovid/data/Mpro/aligned/ --boundPdbs_to_score_pattern ".*-(x12\w+)_bound\.pdb$"
'''