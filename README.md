# MetaPONT: Metagenomic Taxonomy Pipline for ONT sequencing

## Installation

MetaPONT runs Centrifuge and Minimap in a docker container. For the installation a working Docker installation is
required (https://docs.docker.com/get-docker/).

### 1. Download this repository.

``` 
git clone 
cd metapont
```

### 2. Build Docker Image

```
docker build -t metapont .
```

### 3. Run Docker Container

```
docker run metapont --help
```

## Database building

To build a usable database, you need a Centrifuge database. Please follow the instructions
on https://github.com/DaehwanKimLab/centrifuge

### 1. Conversion Table

To get the relationship SeqID->taxID run:

```
centrifuge-inspect --conversion-table <base> > conversionTable.txt
```

This file can be very redundant, so let's go ahead and uniq it:

```
cat conversionTable.txt | sort | uniq > conversionTable_tmp.txt
mv conversionTable_tmp.txt conversionTable.txt
```

### 2. Build a fasta file from your Centrifuge Database:

```
nohup centrifuge-inspect <base>
```

Base is the short name of your database (it's the equivalent of p+h+v, p_compressed, etc. on the Centrifuge GitHub). We
use nohup here because this can take some time. You can of course use alternatives. In the case of nohup be sure to
rename nohup.out to for example p+h+v_all_seqs.fasta.

```
mv nohup.out <base>.fasta
```

### 3. We will now build an index with the tool cdbfasta (https://github.com/gpertea/cdbfasta):

```
nohup cdbfasta <base>.fasta
```

### 4. Build Database

In the next step we will build the taxID-fasta-files and gzip them. Please be aware that this will need a lot of disk
space and run for a long time, depending on the database size. The skript `mmpDBbuilder.py` will generate the fasta
files.

```
nohup python3 mmpDBbuilder.py </path/to/conversiontable> </path/to/fasta_index> <processes>
```

* `</path/to/conversiontable>` absolute path to output of 1.
* `</path/to/fasta_index>` absolute path to output of 3.
* `<processes>` is the number of subprocesses you want to start (how many files should be build at the same time)

### (5. Clean up)

If you are done and sure, that you do not want to redo certain steps of the procedure you can remove the output of step
2 and 3 (i.e. the big fasta file, the cdbfasta index, and all nohup.out files). MeTaPONT does not need these files to
work.

## Usage

Run `docker run metapont --help` to get the Information below.

```
Docker run -v /path/to/database:/database -v /path/to/input:/input -v /path/to/output/directory:/output ContainerName [Parameters]
```

* Change `/path/to/database` to the absolute path of the database directory you want to use.
* Change `/path/to/input` to your absolute path of the input fastq file or a directory that contains fastq files (all
  subdirectories will be searched for *.fastq-files and they will be the input).
* Change `/path/to/output` to the absolute path of the directory you want the output in.

* `-c` just Centrifuge will be used [Default: Centrifuge and Minimap2 will be used].
* `-k <Int>` max number of TaxIDs returned by Centrifuge, only important if -c [Default: 5].
* `-t <Int>` max number of threads used by Centrifuge and MMP2 [Default: 1].
* `--threshold <Int>` taxIDs in centrifuge_out.tsv are omitted when score is lower than threshold [Default: 150].
* `--filter <Int:Int>` thresholds for minimap2 output. First int is the normalized Smith-Waterman-AS threshold, second
  is coverage threshold (0-100). [Default: 1000:50]
* `--filter-benchmarking <int,...,int:int,int:...>` two lists of minimap cutoff values of type int. Every combination
  will be saved.
* `--normalize < 0 | 1 >` decides if Smith Waterman score should be normalized with the alignment length (1) or not (
  0) [Default: 1].
* `--redundance <Int>` readIDs with centrifuge hits to at least `redundance` taxIDs will be dropped, only if not
  -c [Default: 50].
* `--verbose` gives more files as output (mostly for debugging purposes).

