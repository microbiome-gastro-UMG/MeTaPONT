#!/usr/bin/env python3
# transforms the data obtained by minimap

import os
import sys
import pandas as pd
import warnings


def thresholds(as_threshold, cov_threshold, mmp_df, output_dir):
    df = mmp_df.copy()
    # print(f"AS:{as_threshold} cov:{cov_threshold} dflength{len(df)}")
    # print(f"\t 12 dflength{len(df)}")
    output_path = output_dir + '/readIDTaxID'
    if int(as_threshold) > 0:
        df.drop(df[df.AS < int(as_threshold)].index, inplace=True)
        output_path = output_path + 'AS' + str(as_threshold)
        # print(f"\t 18 dflength{len(df)}")

    if 100 >= int(cov_threshold) > 0:
        df.drop(df[(df['alignment_length'] / df['query_length']) * 100 < int(cov_threshold)].index, inplace=True)
        output_path = output_path + 'Cov' + str(cov_threshold)
        # print(f"\t 23 dflength{len(df)}")

    df['readID'] = df['readID'].astype('str')
    df = df.sort_values('readID')
    # print(f"\t 26 dflength{len(df)}")

    df[['readID', 'taxID']].to_csv(output_path + '.txt', sep='\t', index=False)


def benchmarking(mmp_thresholds_benchmarking, mmp_df, output_dir):
    try:
        as_thresholds = mmp_thresholds_benchmarking.split(':')[0].split(',') + [0]
        cov_thresholds = mmp_thresholds_benchmarking.split(':')[1].split(',') + [0]
    except IndexError:
        print(f"WRONG INPUT FORMAT FOR --filter-benchmarking!{mmp_thresholds_benchmarking}")
    else:
        for alignment_score in as_thresholds:
            for coverage in cov_thresholds:
                thresholds(as_threshold=int(alignment_score), cov_threshold=int(coverage), mmp_df=mmp_df,
                           output_dir=output_dir)


if __name__ == '__main__':
    print("read file")
    output_dir = sys.argv[1]
    mmp_thresholds = sys.argv[2]
    mmp_thresholds_benchmarking = sys.argv[3]
    normalize = sys.argv[4]
    paf_files = os.listdir(output_dir + '/minimap2output/')

    print("concatenate Minimap 2 output, correct taxids, get Alignment Scores")
    all_dfs = []
    for file in paf_files:
        if not file.endswith(".paf"):
            continue
            
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore')
            tmp_df = pd.read_csv(output_dir + '/minimap2output/' + file, index_col=False, on_bad_lines='warn', sep=' |\t', header=None,
                             names=['readID', 'query_length', 'query_start', 'query_end',
                                    'query_strand',
                                    'taxID', 'target_length', 'target_start', 'target_end',
                                    'matches', 'alignment_length', 'Qscore',
                                    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
            
        tmp_df['taxID'].values[:] = int(file.split(".")[0])  # set taxID to taxID
        tmp_df['alignment_length'] = pd.to_numeric(tmp_df['alignment_length'], errors='coerce')
        tmp_df['query_length'] = pd.to_numeric(tmp_df['query_length'], errors='coerce')

        # get alignment scores from tag AS:i:
        tmp_df['AS'] = 'AS:i:0'  # add new column for Alignment scores
        tmp_df.columns = tmp_df.columns.get_level_values(0)
        for samcol in range(1, 11):
            samcol = str(samcol)
            idx = tmp_df[samcol].astype('str').str.startswith('AS:i:', na=False)
            tmp_df.loc[idx, 'AS'] = tmp_df.loc[idx, samcol]

        all_dfs.append(tmp_df[['readID', 'taxID', 'matches', 'alignment_length', 'AS', 'query_length']])
    mmp_df = pd.concat(all_dfs, ignore_index=True, sort=False, copy=False)

    print("drop duplicates, put highest score in readID_TaxID")
    mmp_df['readID'] = mmp_df['readID'].astype('str')  # readID to string
    mmp_df['AS'] = mmp_df['AS'].map(lambda x: x.lstrip('AS:i:')).astype(
        'int')  # remove leading AS:i: in AS column, cast to int
    mmp_df.drop(mmp_df[mmp_df.AS <= 0].index, inplace=True)  # drop score 0
    mmp_df.drop(mmp_df[mmp_df.alignment_length <= 0].index, inplace=True)  # drop alignment_length 0
    mmp_df.dropna(subset=['AS', 'alignment_length', 'query_length'], inplace=True)  # Drop NA

    if normalize == "true":  # normalize
        mmp_df['AS'] = mmp_df['AS'].astype('float64') / (mmp_df['alignment_length'].astype('float64')) * 1000
        mmp_df.round({'AS': 0})
        mmp_df['AS'] = mmp_df['AS'].astype('int')

    # drop duplicates
    mmp_df.drop_duplicates(inplace=True, ignore_index=True)

    # print(f"\t mmp_thresholds_benchmarking {mmp_thresholds_benchmarking} {type(mmp_thresholds_benchmarking)}")

    if mmp_thresholds_benchmarking != "0":
        mmp_df.to_csv(output_dir + '/mmp2_out.tsv', sep='\t', index=False)

        mmp_df.sort_values('AS', ascending=False, kind='mergesort', inplace=True)
        mmp_df.drop_duplicates(['readID'], inplace=True)

        print("Do benchmarking.")
        benchmarking(mmp_thresholds_benchmarking, mmp_df=mmp_df, output_dir=output_dir)

    else:
        # print(f"\t 92 mmp_thresholds{mmp_thresholds}")
        as_threshold = int(mmp_thresholds.split(':')[0])
        cov_threshold = int(mmp_thresholds.split(':')[1])

        mmp_df.to_csv(output_dir + '/mmp2_out.tsv', sep='\t', index=False)

        mmp_df.sort_values('AS', ascending=False, kind='mergesort', inplace=True)
        mmp_df.drop_duplicates(['readID'], inplace=True)

        print(f"Filter with thresholds and build readIDTaxIDAS{as_threshold}Cov{cov_threshold}.txt")
        thresholds(as_threshold, cov_threshold, mmp_df=mmp_df, output_dir=output_dir)
