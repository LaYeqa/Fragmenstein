
import os
from tempfile import NamedTemporaryFile
from typing import List

from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem import AllChem

from fragmenstein import Igor
from fragmenstein import Victor
from fragmenstein.external import ExternalToolImporter
from fragmenstein.protocols.dataModel.compound import Compound
from fragmenstein.protocols.steps.combineMerge_abstract import ErrorInComputation, CombineMerge_Base
from fragmenstein.protocols.steps.combineMerge_fragmensteinDefault import CombineMerge_FragmensteinDefault
from fragmenstein.protocols.steps.hitsPreprocess_fragmentationBrics import HitsPreprocess_fragmentationBRICS
from fragmenstein.protocols.steps.minimizePdbComplex_pyrosetta import MinimizePDBComplex_pyrosetta
from fragmenstein.protocols.xchem_info import Xchem_info
from fragmenstein.scoring._fragmenstein_scoring import _FragmensteinScorer
from fragmenstein.utils.config_manager import ConfigManager
from fragmenstein.utils.pdb_utils import PdbDistanceManager


class CombineMerge_DeLinkerDefault( CombineMerge_Base  ):



    @staticmethod
    def get_examples_combine_params():
        data_dir = os.path.abspath(os.path.join(Xchem_info.examples_dir, "hit_mols"))
        fnames = [os.path.join(data_dir, "Mpro-x0678.mol"), os.path.join(data_dir, "Mpro-x0434.mol")]
        list_of_fragments = [Compound.MolFromFile(fname, fname.split("-")[-1].split(".")[0]) for fname in fnames]

        list_of_fragments= [ Compound.DeleteSubstructs( mol, Chem.MolFromSmiles("O=CN"))  for mol in list_of_fragments]
        list_of_fragments[0] = Compound.GetMolFrags(list_of_fragments[0])[0]
        list_of_fragments[1] = Compound.GetMolFrags(list_of_fragments[1])[1]
        list_of_fragments = [list_of_fragments]
        return dict(
            list_of_fragments= list_of_fragments
        )


    def __init__(self, random_seed=None, gpu_id=None, number_of_generation_per_valid=1, n_atomPairs_attemps=1, *args, **kwargs):

        super().__init__( *args, **kwargs)

        self.random_seed = random_seed
        from fragmenstein.external.DeLinker.DeLinkerWrapper import DeLinkerWrapper
        self.delinker = DeLinkerWrapper( number_of_generation_per_valid=number_of_generation_per_valid,
                         n_atomPairs_attemps=n_atomPairs_attemps, n_cores=1, gpu_id=gpu_id,
                         interactive=False, random_seed= self.random_seed)




    example_fragments = [b"\xef\xbe\xad\xde\x00\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x0b\x00\x00\x00\x80\x01\x07\x00h\x00\x00\x00\x03\x01\x02\x06\x00(\x00\x00\x00\x03\x04\x08\x00(\x00\x00\x00\x03\x02\x06\x00`\x00\x00\x00\x02\x02\x06\x00`\x00\x00\x00\x02\x02\x06@(\x00\x00\x00\x03\x04\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x0b\x01\x00 \x02\x01(\x02\x03\x01\x00\x04\x03\x00\x05\x04\x00\x06\x05h\x0c\x07\x06h\x0c\x08\x07h\x0c\t\x08h\x0c\n\th\x0c\n\x05h\x0c\x17\x01\x00\x00\x00\x01\x00\x00\x00\x00\x0b1\x08\n\xc1\x98n*@\x8dW\x9a\xc2B`\x07\xc1^\xba\xa9?\xa40\x9a\xc2\xc5 \x16\xc1D\x8b\x0c?\x89\xc1\x99\xc2\xc3\xf5\xe0\xc0\x08\xac\\?\xa4p\x9a\xc2\xd3M\xce\xc0\xfe\xd4x?q=\x9d\xc2h\x91\xed\xc0\x8d\x97\x9e?^z\x9f\xc2-\xb2\x05\xc1\x85\xeb\x91>\x83@\xa0\xc2\x1f\x85\x13\xc1\xdd$\x06?\xb2]\xa2\xc2'1\x12\xc1\x1f\x85\xdb?\x06\xc1\xa3\xc2)\\\x03\xc1\\\x8f*@\xa2\x05\xa3\xc2=\n\xeb\xc0\x0c\x02\x1b@\xf6\xe8\xa0\xc2\x16", b'\xef\xbe\xad\xde\x00\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\x80\x01\x06\x00`\x00\x00\x00\x01\x03\x10\x00`\x00\x00\x00\x05\x01\x08\x00(\x00\x00\x00\x03\x02\x08\x00(\x00\x00\x00\x03\x02\x0b\x01\x00\x00\x02\x01\x08\x02\x03\x01\x08\x02\x17\x01\x00\x00\x00\x01\x00\x00\x00\x00\x041\x08\x80\xc1\x81\x95\x8f@!\xf0\x9f\xc2\x93\x18t\xc1\xd7\xa3\xa8@\xaa1\x9d\xc2b\x10p\xc1\x89A\xd4@\xf6\xe8\x9d\xc2u\x93\x80\xc1\x00\x00\xa0@s\xe8\x9a\xc2\x16']
    example_delkinker = [b'\xef\xbe\xad\xde\x00\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x16\x00\x00\x00\x16\x00\x00\x00\x80\x01\x06\x00`\x00\x00\x00\x01\x03\x10\x00 \x00\x00\x00\x06\x08\x00(\x00\x00\x00\x03\x02\x08\x00(\x00\x00\x00\x03\x02\x06\x00h\x00\x00\x00\x03\x03\x01\x06\x00h\x00\x00\x00\x03\x03\x01\x10\x00 \x00\x00\x00\x02\x06\x00(\x00\x00\x00\x03\x04\x07\x00(\x00\x00\x00\x03\x03\x07\x00h\x00\x00\x00\x03\x01\x02\x07\x00h\x00\x00\x00\x03\x02\x01\x06@(\x00\x00\x00\x03\x04\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@(\x00\x00\x00\x03\x04\x06\x00`\x00\x00\x00\x02\x02\x06\x00`\x00\x00\x00\x02\x02\x06\x00(\x00\x00\x00\x03\x04\x07\x00h\x00\x00\x00\x03\x01\x02\x08\x00(\x00\x00\x00\x03\x02\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x0b\x00\x01\x00\x01\x02\x08\x02\x01\x03\x08\x02\x01\x04\x00\x04\x05\x08\x02\x05\x06\x00\x06\x07\x00\x07\x08(\x02\x08\t \x07\n \n\x0b \x0b\x0ch\x0c\x0c\rh\x0c\r\x0eh\x0c\x0e\x0f\x00\x0f\x10\x00\x10\x11\x00\x11\x12 \x11\x13(\x02\x0e\x14h\x0c\x14\x15h\x0c\x15\x0bh\x0c\x14\x01\x06\x0b\x15\x14\x0e\r\x0c\x17\x01\x00\x00\x00\x01\x00\x00\x00\x00\x16\xcfK\x80\xc1\xcf\x9f\x8e@\x93\x12\xa0\xc2<|r\xc1\xaf\xa7\xa5@\xed_\x9d\xc2\xfbQo\xc1\x1c\x81\xd4@\x17\xe8\x9d\xc2\xb4\x0e\x80\xc11"\xa0@\x8e\xea\x9a\xc2\x80iY\xc1I\x12\x8b@\xf1\xee\x9c\xc2\xff\x7fL\xc1\x02bp@J\xc5\x9e\xc2\x8b\xbeO\xc1\x87\xc3k@\xaf`\xa2\xc2\xd9=3\xc1&Ud@\x830\xa3\xc2\xa2%\'\xc1\xb8\xe0\x93@\xff\x0f\xa3\xc2\xb9\x13/\xc1\xf5\xd8\xbb@bF\xa2\xc28H*\xc1zr\x13@\xb2\x12\xa4\xc2\x07\x1b\x15\xc1\x9f\xfc\xe7?En\xa3\xc2\x00L\x14\xc1\xa3\xc0\n?\xeeA\xa2\xc2\x1e\xfb\x04\xc1eL|>\x9cN\xa0\xc2\xe8)\xec\xc03\xe9\x9b?\x89\x8b\x9f\xc2/n\xcd\xc0\x8bc|?\'I\x9d\xc2[y\xe1\xc0\xfdhH?\xf4\x80\x9a\xc2\x19\xd5\x06\xc1\xdb\x0e\xaa?|-\x9a\xc2\xe5i\n\xc1Gz.@\xc2T\x9a\xc2\xd9?\x16\xc1\xd14\x0c?\xdf\xc2\x99\xc2zM\xea\xc0\xd3$\x1b@S\xf2\xa0\xc2\x03\x8a\x04\xc1\xb6\x06.@,\xe2\xa2\xc2\x16', b"\xef\xbe\xad\xde\x00\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x1a\x00\x00\x00\x80\x01\x06\x00`\x00\x00\x00\x01\x03\x10\x00 \x00\x00\x00\x06\x08\x00(\x00\x00\x00\x03\x02\x08\x00(\x00\x00\x00\x03\x02\x06@(\x00\x00\x00\x03\x04\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@(\x00\x00\x00\x03\x04\x06\x00h\x00\x00\x00\x03\x03\x01\x06\x00h\x00\x00\x00\x03\x03\x01\x06\x00`\x00\x00\x00\x02\x02\x08\x00(\x00\x00\x00\x03\x02\x06@(\x00\x00\x00\x03\x04\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@(\x00\x00\x00\x03\x04\x06\x00`\x00\x00\x00\x02\x02\x06\x00`\x00\x00\x00\x02\x02\x06\x00(\x00\x00\x00\x03\x04\x07\x00h\x00\x00\x00\x03\x01\x02\x08\x00(\x00\x00\x00\x03\x02\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x0b\x00\x01\x00\x01\x02\x08\x02\x01\x03\x08\x02\x01\x04\x00\x04\x05h\x0c\x05\x06h\x0c\x06\x07h\x0c\x07\x08h\x0c\x08\th\x0c\t\n \n\x0b(\x02\x0b\x0c\x00\x0c\r\x00\r\x0e \x0e\x0fh\x0c\x0f\x10h\x0c\x10\x11h\x0c\x11\x12\x00\x12\x13\x00\x13\x14\x00\x14\x15 \x14\x16(\x02\x11\x17h\x0c\x17\x18h\x0c\t\x04h\x0c\x18\x0eh\x0c\x14\x02\x06\x04\t\x08\x07\x06\x05\x06\x0f\x10\x11\x17\x18\x0e\x17\x01\x00\x00\x00\x01\x00\x00\x00\x00\x19\xc3\xe2~\xc1\xa1-\x8d@>\x04\xa0\xc2a\x12s\xc12\x1f\xa6@\x8d2\x9d\xc2\x10\x08o\xc1\xe2V\xd4@\xaf\xd8\x9d\xc2N\x95\x81\xc1\x7f,\xa3@\xc9\xfa\x9a\xc2\xee\xe5[\xc1\xd1\x96\x8c@6\xe8\x9b\xc2\x07;[\xc1a\x08\x8a@3\x1a\x99\xc2Z\x11K\xc1\x8cKh@}\xc4\x97\xc2S\x1a;\xc1\xf9\x11@@\x00:\x99\xc2\xf14;\xc1\x99\x06E@\xdc\x01\x9c\xc2\xe9GK\xc1\x0c\x94q@\xbfj\x9d\xc2`\x0cI\xc1d\x81w@1`\xa0\xc2\x0f{9\xc1\xd6\xa3J@\x14\x95\xa1\xc2:\x983\xc1\tNM@@~\xa4\xc2\xe4\xc9%\xc1|\xc2\x06@\t(\xa5\xc2\xba\xf4\x13\xc1\xcb>\xe1?\xda\x98\xa3\xc2/\xca\x13\xc1\xd9\x94\x03?\x1cT\xa2\xc2\xce\x19\x05\xc1G>\x80>tI\xa0\xc2n\x8f\xec\xc0\x06L\x9d?G\x87\x9f\xc2\xda\xa3\xcd\xc0G\xa2\x7f?\xe4F\x9d\xc2\xee\x85\xe1\xc0\xe4UF?B\x80\x9a\xc2\x9b\xc3\x06\xc1\xbe\xfe\xa9?E*\x9a\xc2\xd7#\n\xc1p\x8c.@jQ\x9a\xc2\xe0D\x16\xc1$\x89\r?~\xc1\x99\xc2.\xce\xea\xc07\xe5\x1b@t\xef\xa0\xc2'-\x04\xc1\xd9\x06-@y\xf7\xa2\xc2\x16", b'\xef\xbe\xad\xde\x00\x00\x00\x00\x0c\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x1b\x00\x00\x00\x80\x01\x06\x00`\x00\x00\x00\x01\x03\x10\x00 \x00\x00\x00\x06\x08\x00(\x00\x00\x00\x03\x02\x08\x00(\x00\x00\x00\x03\x02\x06@(\x00\x00\x00\x03\x04\x10@(\x00\x00\x00\x03\x02\x06@h\x00\x00\x00\x03\x03\x01\x07`*\x00\x00\x00\x01\x03\x04\x07\x00h\x00\x00\x00\x03\x02\x01\x06\x00(\x00\x00\x00\x03\x04\x08\x00(\x00\x00\x00\x03\x02\x07\x00h\x00\x00\x00\x03\x02\x01\x06@(\x00\x00\x00\x03\x04\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@(\x00\x00\x00\x03\x04\x06\x00`\x00\x00\x00\x02\x02\x06\x00`\x00\x00\x00\x02\x02\x06\x00(\x00\x00\x00\x03\x04\x07\x00h\x00\x00\x00\x03\x01\x02\x08\x00(\x00\x00\x00\x03\x02\x06@h\x00\x00\x00\x03\x03\x01\x06@h\x00\x00\x00\x03\x03\x01\x06@(\x00\x00\x00\x03\x04\x06\x00(\x00\x00\x00\x02\x04\x07\x00(\x00\x00\x00\x02\x03\x0b\x00\x01\x00\x01\x02\x08\x02\x01\x03\x08\x02\x01\x04\x00\x04\x05h\x0c\x05\x06h\x0c\x06\x07h\x0c\x07\x08 \x08\t \t\n(\x02\t\x0b \x0b\x0c \x0c\rh\x0c\r\x0eh\x0c\x0e\x0fh\x0c\x0f\x10\x00\x10\x11\x00\x11\x12\x00\x12\x13 \x12\x14(\x02\x0f\x15h\x0c\x15\x16h\x0c\x07\x17h\x0c\x17\x18 \x18\x19(\x03\x17\x04h\x0c\x16\x0ch\x0c\x14\x02\x05\x04\x05\x06\x07\x17\x06\r\x0e\x0f\x15\x16\x0c\x17\x01\x00\x00\x00\x01\x00\x00\x00\x00\x1ab\xf3\x80\xc1uJ\x90@\x80\x07\xa0\xc2\xf9Tt\xc1\n\xf3\xa6@HF\x9d\xc2w\xa8o\xc1\xed@\xd5@H\xcf\x9d\xc2\xd2\xd9\x80\xc1J\xdc\xa1@\xc8\xce\x9a\xc2j\x0f]\xc1c\xcf\x88@\xc3\xfa\x9c\xc2k\xd3Y\xc1M\xd4C@#\xb2\x9a\xc2x\nG\xc1\xa1M\x0f@\xbcr\x9c\xc2\xf0\xddC\xc1d\x937@\xd3\xce\x9e\xc2Xa5\xc1\xbe\xc6\x16@:\xae\xa0\xc2\x91\x817\xc1\xc93\x19@\xb2\x8a\xa3\xc2\xdcMI\xc1\xbb\x1a\'@%\xa3\xa4\xc2E\x17%\xc1\xdef\x07@=$\xa5\xc2\x05`\x12\xc1XU\xda?\xd3\xbd\xa3\xc2\x9a\x0c\x13\xc17\xa1\xfb>hY\xa2\xc2\xc2\xda\x04\xc1\x18/|>\xabA\xa0\xc2\xd7!\xec\xc0\x93\x01\x9d?Q\x82\x9f\xc2\xa7|\xcd\xc0ay\x80?0?\x9d\xc2?\xa6\xe1\xc0\x1a6H?\xfez\x9a\xc2d\xe7\x06\xc1Z#\xaa?\xc4)\x9a\xc2\x93w\n\xc1\xa3\x83.@JS\x9a\xc2\x8fV\x16\xc1o|\x0c?\x97\xc1\x99\xc2\xff&\xea\xc0hn\x1b@\xd1\xed\xa0\xc2\x16S\x03\xc1\xfd%+@\x80\x05\xa3\xc2"oO\xc1\xb4t\x80@x\x19\x9f\xc2\xa0+M\xc1\xfbW\x9d@\xf0U\xa1\xc2\xb3^K\xc1\xae\xa1\xb4@\x14\x1f\xa3\xc2\x16']

    def tryOneGeneric(self, merge_id, templateFname, fragments: List[Compound], wdir, *args, **kwargs):

        assert len(fragments) == 2, "Error, DeLinker only works for pairs of compounds"

        final_outdir =  os.path.join(wdir, merge_id)
        if not os.path.exists(final_outdir):
            os.mkdir( final_outdir ) #Required, as here is where _tryOneGeneric will save checkpoint

        fragments  = list( fragments )
        for i, frag in enumerate(fragments):
            try:
                Chem.MolToMolFile( frag, os.path.join(final_outdir, "frag_%d.mol"%i))
            except Chem.rdchem.MolSanitizeException:
                pass

        # import matplotlib.pyplot as plt
        # from rdkit.Chem import Draw
        # plt.imshow(Draw.MolsToGridImage(fragments, molsPerRow=1)); plt.show()

        RDLogger.DisableLog('rdApp.warning')
        proposed_mols = self.delinker.link_molecule_pair(*fragments)
        RDLogger.EnableLog('rdApp.warning')

        # proposed_mols = proposed_mols[:20]
        # print( [Chem.MolToSmiles(mol) for mol in proposed_mols] )
        # import matplotlib.pyplot as plt
        # from rdkit.Chem import Draw
        # for i in range(len(proposed_mols)):
        #     plt.imshow(Draw.MolsToGridImage([proposed_mols[i]], molsPerRow=1)); plt.show()

        # proposed_mols = list(map(Chem.Mol, type(self).example_delkinker))


        placed_results = []

        w_DeLinker = Chem.SDWriter( os.path.join(final_outdir, "delinker_mols.sdf"))

        minimizer = MinimizePDBComplex_pyrosetta(templateFname, atom_constrain_filter=lambda atom: atom.HasProp("is_original_atom"))

        def minimizeMol(molId, mol ):
            mol, metadata_dict = minimizer.minimize(mol, molId=molId, outdir=wdir, reference_fragments=fragments)
            metadata_dict = _FragmensteinScorer.old_scoring_fun(metadata_dict)[-1]
            metadata_dict = _FragmensteinScorer.new_scoring_fun(metadata_dict)[-1]

            metadata_dict["fragments"] = [ frag.primitiveId for frag in fragments]
            metadata_dict["ref_pdb"] = templateFname

            generated_molecule = Compound( mol, molId=molId, parents= fragments)
            generated_molecule.ref_pdb = templateFname
            generated_molecule.metadata = metadata_dict
            generated_molecule.ref_molIds =  metadata_dict["fragments"]

            return  generated_molecule

        for i, proposal in enumerate(proposed_mols):
            w_DeLinker.write(proposal)

            # smi = Chem.MolToSmiles( proposal )

            placed_mols = [ minimizeMol( merge_id+"_"+str(i), proposal) ]

            # ExternalToolImporter.import_tool("pyrosetta", ["pyrosetta"])
            # Victor.work_path = wdir
            # v = Victor(fragments, pdb_filename=templateFname)
            # v.place(smi)#, merging_mode="full")
            # print(v.ddG)

            # placed_mols =  super().tryOneGeneric( merge_id+"_"+str(i), templateFname, fragments, wdir, smi)

            if isinstance(placed_mols,  ErrorInComputation):
                continue
            placed_results +=  placed_mols

        w_DeLinker.close()

        if len(placed_results)>0:
            w_placed = Chem.SDWriter(os.path.join(final_outdir, "placed_mols.sdf"))
            for mol in placed_results:
                w_placed.write(mol)

            w_placed.close()

        print(len(placed_results)); input("enter")
        return placed_results


def test_applyCombine():
    init_params = CombineMerge_DeLinkerDefault.get_examples_init_params()
    init_params["number_of_generation_per_valid"] = 2
    combiner = CombineMerge_DeLinkerDefault( **init_params, use_dask=False, gpu_id=0)
    results = combiner.applyCombine( **CombineMerge_DeLinkerDefault.get_examples_combine_params())
    print("RESULTS applyCombine:")
    print( results)



if __name__ == "__main__":

    print("trying combine")
    test_applyCombine()

    '''

python -m fragmenstein.protocols.steps.combineMerge_DeLinkerDefault

    '''