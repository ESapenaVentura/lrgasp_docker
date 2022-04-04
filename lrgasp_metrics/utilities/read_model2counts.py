#!/usr/bin/env python3

import os
import pandas as pd


def get_counts(tsv_file):
    tsv = pd.read_csv(tsv_file, sep='\t')
    counts = tsv.groupby(tsv.transcript_id.str.strip('"'))['read_id'].nunique()
    name = f"{os.path.dirname(tsv_file)}/{os.path.splitext(os.path.basename(tsv_file))[0]}.counts.tsv"
    counts.to_csv(name, index=True, sep='\t', header=["count_fl"])
    return name
    

