#!/usr/bin/env python3
# transforms the data obtained by centrifuge
import os
import sys
import pandas as pd

if __name__ == '__main__':
    output_dir = sys.argv[1]
    centrifuge_threshold = int(sys.argv[2])
    mode = sys.argv[3]
    redundance = int(sys.argv[4])

    print(f"filter centrifuge_out.tsv with threshold {centrifuge_threshold} and update file")
    df = pd.read_csv(output_dir + '/centrifuge_out.tsv', sep='\t')
    df['score'] = df['score'].astype('int')
    df['taxID'] = df['taxID'].astype('int')
    df.drop_duplicates(inplace=True, ignore_index=True)
    df.drop(df[df.taxID == 0].index, inplace=True)
    df.drop(df[df.score <= 0].index, inplace=True)
    df.drop(df[df.score < centrifuge_threshold].index, inplace=True)
    df.drop_duplicates(inplace=True, ignore_index=True)

    if mode != "c":
        df.to_csv(output_dir + '/centrifuge_out_before_dropping.tsv', sep='\t', index=False)
        print(f"drop reads that are found in at least {redundance} taxIDs.")
        df = df.groupby('readID').filter(lambda x: len(x) < redundance)
        df.to_csv(output_dir + '/centrifuge_out.tsv', sep='\t', index=False)

    else:
        print("-c: Drop duplicates and safe in centrifuge_out.tsv. Keep value with highest Centrifuge Score")
        df.sort_values('score', ascending=False, inplace=True).drop_duplicates(['readID'], inplace=True)
        df.to_csv(output_dir + '/centrifuge_out_unique.tsv', sep='\t', index=False)

        print("make readIDTaxID.tsv")
        readID_taxID = df[['readID', 'taxID']]
        readID_taxID.to_csv(output_dir + '/centrifuge_readIDTaxID.tsv', sep='_', index=False)
