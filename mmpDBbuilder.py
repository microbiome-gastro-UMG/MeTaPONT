#!/usr/bin/env python3
import subprocess
import os
import multiprocessing
import pandas as pd
import timeit
import sys

if __name__ == '__main__':
    conversiontable = sys.argv[1]  # absolute path to conversion table
    fasta_index = sys.argv[2]  # absolute path to cdbfasta index
    processes = int(sys.argv[3])  # number of max processes
    wd = os.path.dirname(fasta_index)  # working directory
    start_taxID = 0  # start taxid, lower taxids will be ignored

    print(f"A usable Database will be build from \n "
          f"conversion table \t {conversiontable}\n "
          f"with fasta index \t {fasta_index}\n")
    print(f"We will start at taxID {start_taxID} and use {processes} subprocesses.")

    time1 = timeit.default_timer()
    df = pd.read_csv(conversiontable, sep='\t', names=['name', 'taxid'])
    df.drop_duplicates(inplace=True)
    df.sort_values(by=['taxid'], inplace=True, kind='mergesort')


    def command(taxid, fasta_index=fasta_index, wd=wd, conversiontable=conversiontable):
        cmd = f"awk '$2=={taxid}' {conversiontable} | cut -f1 | cdbyank {fasta_index} | gzip -9 > {wd}/fastaTaxID/{taxid}.gz; "
        subprocess.run(cmd, input='\n'.join(df[df['taxid'] == taxid]['name'].values), encoding='ascii', shell=True)


    taxids = df['taxid']
    taxids = taxids.drop_duplicates(inplace=False)
    taxids = taxids.drop(taxids[taxids < start_taxID].index, inplace=False).to_list()

    time2 = timeit.default_timer()
    print('building DFs took ', time2 - time1, " s")

    if not os.path.exists(wd + "/fastaTaxID"):
        os.mkdir(wd + "/fastaTaxID")

    pool = multiprocessing.Pool(processes=processes)
    r = pool.map_async(command, iter(taxids))
    pool.close()
    pool.join()
    print('processing', len(taxids), ' taxids took ', timeit.default_timer() - time2)
