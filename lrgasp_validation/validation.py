"""
Validation that is performed:

- All files exist in the path provided
- Schemas path is absolute
- There are json files in the schemas_path
- Entry metadata is validated against schema
- Models.gtf is validated using lrgasp-tools
-

#TODO
- More tests from lrgasp-tools applied
- Validate the challenges
"""

import os
import sys
import json
import argparse
import hashlib
from jsonschema import RefResolver, Draft7Validator
import tarfile


# lrgasp-tools validation
from lrgasp import model_data
from lrgasp import read_model_map_data
from lrgasp.entry_validate import validate_ref_model_and_read_mapping

import JSON_templates

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
ERRORS = []

library_to_metadata = {'ENCFF105WIJ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF028FCL': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF212HLP': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF950ANU': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF003QZT': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF508XUP': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF654SNK': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF970AUV': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF934KDM': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF902FSA': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF104BNW': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF053QEQ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF155CFF': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF146MTW': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF771DIX': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF389XGB': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF600LIU': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF591QYR': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF153SIE': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF178BYM': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF377IEH': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF063ASB': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF489PQQ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF408XXR': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF089IVT': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF542VPN': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF548RZB': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF679LUJ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF997UNC': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF357UQD': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF766OAK': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF198RQU': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF247XJT': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF563QZR': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF112MRR': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF338WQL': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF992WSK': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF370NFS': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF122GKS': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF455RXJ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF875XMU': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF245IPA': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF434SWA': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF620NFT': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF962OWJ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF263YFG': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF585AMS': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF023EXJ': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF737GVV': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF961HLO': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF510ABH': {'species': 'human', 'samples': 'WTC11', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF705IEA': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF073YYF': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF885YGF': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF509GUL': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF822IZD': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF499AVA': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF716HXZ': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF797VHT': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF595GFC': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF571LYR': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF072FJA': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF317BHX': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF854BEI': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF120DLZ': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF804BPC': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF336WGD': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF557WRQ': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF316TNM': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF947MTX': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF438GQV': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF979MUK': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF433QSW': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF379KHH': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF348EXF': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF672BIU': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF918TKZ': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF092GJH': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF923NYH': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF694JLN': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF894DPZ': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF201EVI': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF221SLD': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF145IIO': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF701OIK': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF525JUC': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF413ZWA': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF735HPE': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF743MYM': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF205WPS': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF945KEK': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF372YUA': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF539DBI': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF736JMP': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF082OHO': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF741ZFV': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF304JRO': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF506RNI': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF389YOZ': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF013SGT': {'species': 'human', 'samples': 'H1_mix', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'syn25683372': {'species': 'human', 'samples': 'human_simulation', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'syn25683376': {'species': 'human', 'samples': 'human_simulation', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'syn25683375': {'species': 'human', 'samples': 'human_simulation', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF535DQA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF710FCJ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF310IPO': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF062QXB': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF654JHQ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF110VBJ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'PacBio'}, 'ENCFF356OJC': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF670UEC': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF275RMO': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF942RPL': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF056EOI': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF861WOA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'CapTrap', 'platforms': 'ONT'}, 'ENCFF765AEC': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF914OBQ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF349BIN': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF793LSF': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF412NKJ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF464USM': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'ENCFF824JVI': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF055REA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF104DMI': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF598YQO': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF412UHU': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF335WMC': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF513AEK': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF797PJV': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF850MIB': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF742GCO': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF595TIH': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF717LLT': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'R2C2', 'platforms': 'ONT'}, 'ENCFF521IDK': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF089PFT': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF696TCH': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'ENCFF874VSI': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF005VJA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF564NGV': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF714ZJR': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF667VXS': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF493CBP': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF783PVA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF993JVA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF313VYZ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF078IYM': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF094NZA': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF280DWZ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'PacBio'}, 'ENCFF683TBO': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF429FDN': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF232YSU': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF209ZZU': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF288PBL': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'ENCFF931ICQ': {'species': 'mouse', 'samples': 'ES', 'library_preps': 'cDNA', 'platforms': 'ONT'}, 'syn25683380': {'species': 'mouse', 'samples': 'mouse_simulation', 'library_preps': 'dRNA', 'platforms': 'ONT'}, 'syn25683378': {'species': 'mouse', 'samples': 'mouse_simulation', 'library_preps': 'cDNA', 'platforms': 'Illumina'}, 'syn25683381': {'species': 'mouse', 'samples': 'mouse_simulation', 'library_preps': 'cDNA', 'platforms': 'PacBio'}}


def full_path_dir(path: str):
    if not os.path.isabs(path) and not os.path.isdir(path):
        raise ValueError("Provided path is not a full path")
    return path

def is_file(path: str) -> str:
    if not os.path.isfile(path):
        raise ValueError("Provided path is not pointing to any file")
    return path


def string_to_list(challenges):
    return challenges.split(" ")


def parse_arguments(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument("-i", "--input-gz-file", help="Input file path to the user generated files, in tar.gz format",
                        required=True)
    parser.add_argument("-x", "--experiment", help="Experiment JSON document", required=False)
    parser.add_argument("-s", "--schemas-path", help="Path to the JSON schemas", required=False,
                        default=f"{SCRIPT_PATH}/JSON_TEMPLATES", type=full_path_dir)
    parser.add_argument("-o", "--output-path", help="Output directory", required=True, type=str)
    parser.add_argument("-g", "--gtf-filename", help="GTF filename", required=False, type=str)
    parser.add_argument("-r", "--read-model-map-filename", help="Read model map data filename", required=False, type=str)
    parser.add_argument("-m", "--manifest", help="Please use this argument if a manifest.json file is provided",
                        required=False, action='store_true')
    parser.add_argument("-c", "--challenges", help="List of OEB challenges selected. If not provided, all possible will be selected", required=False,
                        type=string_to_list)
    args = parser.parse_args()
    return args


def schemas_are_in_path(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if "experiment.json" not in files:
        return False
    return True


def load_schemas_store(schemas_path: str) -> dict:
    files = [f for f in os.listdir(schemas_path) if os.path.isfile(os.path.join(schemas_path, f))]
    schemas = []
    for f in files:
        try:
            schemas.append(json.load(open(f"{schemas_path}/{f}", 'r')))
        except:
            ERRORS.append(f"Could not load {f}, not a recognised JSON entity")
    # Transform schemas loaded into store
    store = {schema['$id']: schema for schema in schemas}
    return store


def validate_schemas(schema_store, schemas_path, experiment):
    # Build the reference resolver and the validators
    resolver = RefResolver(referrer=schema_store, base_uri=f"file://{schemas_path}/")
    experiment_entry = Draft7Validator(schema_store.get('experiment.json'), resolver=resolver)

    # Iterate the errors and append them to our error log
    for error in experiment_entry.iter_errors(experiment):
        ERRORS.append(f"Value {error.message}")


def validate_bed_file(bed_path):
    """
    Read the bed file and check for:
        - BED file contains at least 3 columns separated by tabs
        - All rows have the same number of columns (size)
    :param bed_path: Path to the CAGE-peaks BED file
    :return:
    """
    with open(bed_path, "r") as f:
        bed = f.readline().split('\t')
        row_one_length = len(bed)
        i = 1
        if len(bed) == 1:
            ERRORS.append(f"CAGE-peaks file columns should be separated by tabs. File used: {bed_path}")
        elif len(bed) < 3:
            ERRORS.append(f"CAGE-peaks file should contain at least 3 columns. File used: {bed_path}")
        else:
            if not all(len(line.split('\t')) == row_one_length for line in f):
                ERRORS.append(f"CAGE-peaks file should have the same amount of columns per row. File used: {bed_path}")


def get_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_md5_files(md5_list_path:str = "static_md5_list.txt"):
    static_md5_map = {}
    with open(md5_list_path, 'r') as f:
        content = f.read().splitlines()
        static_md5_map = {line.split("(")[1].split(") = ")[0]: line.split("(")[1].split(") = ")[1] for line in content}
    return static_md5_map

def check_static_checksums(static_folder):
    files = [f for f in os.listdir(static_folder) if os.path.isfile(os.path.join(static_folder, f))]
    md5_map = {f: get_md5(os.path.join(static_folder, f)) for f in files}
    checked_md5 = read_md5_files()
    for file in md5_map.keys():
        if checked_md5.get(file, '') != md5_map.get(file,''):
            ERRORS.append(f"MD5 checksum failed for file {file}.")


def extract_files_tar_gz(input_file_path: str, output_path: str) -> None:
    tar = tarfile.open(input_file_path, 'r:gz')
    for f in tar:
        try:
            tar.extract(f)
        except IOError:
            print(f"File {f.name} is already in repository")
    tar.close()


def define_parameters_from_manifest(manifest_path: str) -> tuple:
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    return manifest['experiment_json'], manifest['gtf_input'], manifest['read_model_map']


def validate_library_to_metadata(experiment_json):
    metadata = library_to_metadata[experiment_json['libraries']]
    for key in metadata.keys():
        if metadata[key] != experiment_json[key]:
            ERRORS.append(f"Metadata is inconsistent; for library {experiment_json['libraries']}, the {key} value in the experiment.json is expected to be {metadata[key]}")


def challenges_are_valid(challenges, experiment_json):
    for challenge in challenges:
        split_challenge = challenge.split('_')[:2]
        split_challenge.extend(challenge.split('_')[2].split('-'))
        if experiment_json.get('library_preps', '') not in split_challenge[2]:
            ERRORS.append(f'Library preparation in challenge {challenge} and metadata provided in experiment.json is not consistent; please ensure you selected the proper library preparation.')
        if experiment_json.get('platforms', '') not in split_challenge[3]:
            ERRORS.append(f'Sequencing platform in challenge {challenge} and metadata provided in experiment.json is not consistent; please ensure you selected the proper sequencing platform.')
        length = experiment_json.get('data_category', 'N_N').split("_")
        length = f"{length[0][0]}{length[1][0]}".upper()
        if length not in split_challenge[4]:
            ERRORS.append(f'Read length in challenge {challenge} and metadata provided in experiment.json is not consistent; please ensure you selected the proper read length.')


def main(challenges: str, input_file_path: str, experiment_name: str, schemas_path: str, output: str, gtf_filename:str,
         read_model_map_filename:str, manifest) -> int:

    input_path = os.path.dirname(input_file_path)

    try:
        extract_files_tar_gz(input_file_path, input_path)
    except Exception as e:
        sys.exit(f"Input tar.gz file was not found or couldn't be opened: {input_file_path}: Error {e}")

    if not manifest and not all([experiment_name, gtf_filename, read_model_map_filename]):
        sys.exit("Either the manifest or the filename for all files must be provided.")

    manifest_path = os.path.join(input_path, 'manifest.json')

    # The manifest takes priority when defining
    try:
        if manifest:
            experiment_name, gtf_filename, read_model_map_filename = define_parameters_from_manifest(manifest_path)
    except:
        sys.exit("Manifest was either not found or contains invalid fields. Please review the path and/or the fields within the manifest")

    experiment_path = os.path.join(input_path, experiment_name)
    gtf_path = os.path.join(input_path, gtf_filename)
    read_model_map_path = os.path.join(input_path, read_model_map_filename)

    # Validation step 1: Schemas
    # Validation step 1.1: Ensure all schemas are stored in the path provided
    if not schemas_are_in_path(schemas_path):
        ERRORS.append(f"Couldn't find schemas in the directory provided: {schemas_path}")

    # Validation step 1.2: Load schema files as an store
    store = load_schemas_store(schemas_path)

    # Validation step 1.3: Load user entry and experiment instances
    experiment = json.load(open(experiment_path, "r"))

    # Validation step 1.4: Validate metadata schema against instances provided
    validate_schemas(store, schemas_path, experiment)


    # Validation step 2: Ensure contents are ok

    # Validate ref model experiment
    try:
        models = model_data.load(gtf_path)
        read_model_map = read_model_map_data.load(read_model_map_path)
        validate_ref_model_and_read_mapping(models, read_model_map)
    except Exception as ex:
        ERRORS.append(f"Error found during ref model experiment validation: {ex}")
    # TODO: apply more tests from https://github.com/LRGASP/lrgasp-submissions/tree/master/tests

    # Validation step 2.1: Ensure consistency. The library used must coincide with the challenge ids and the species
    validate_library_to_metadata(experiment)

    # Validation step 3: Generate participant dataset
    # To generate the participant datasets, we will be using the example code from https://github.com/inab/TCGA_benchmarking_dockers

    data_id = f"LRGASP_{experiment['experiment_id']}_{experiment['software']['name'].lower()}"

    if not challenges:
        # TODO fix this for docker runs. For now will be focusing on OEB implementation
        ERRORS.append("Challenges must be specified!")
        challenges = [""]
    else:
        challenges_are_valid(challenges, experiment)

    validated = False if ERRORS else True
    output_json = JSON_templates.write_participant_dataset(data_id, "OEBC010", challenges, experiment['software']['name'].lower(),
                                                               validated)
    with open(output, 'w') as f:
        json.dump(output_json, f, sort_keys=True, indent=4, separators=(',', ': '))


    if not ERRORS:
        sys.exit(0)
    else:
        formatted_errors = "\n\t- ".join(ERRORS)
        sys.exit(f"ERROR: Submitted data does not validate! The following errors were found: \n\t- {formatted_errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parse_arguments(parser)
    main(args.challenges, args.input_gz_file, args.experiment, args.schemas_path, args.output_path, args.gtf_filename,
         args.read_model_map_filename, args.manifest)