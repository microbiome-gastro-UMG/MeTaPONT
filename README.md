# MetaPONT: Metagenomic Taxonomy Pipeline for ONT sequencing

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

## Build Database

A prebuild library (from the 2018 procaryotic centrifuge library) can be downloaded from here:  https://owncloud.gwdg.de/index.php/s/QFWoe44UKYGrbGQ

For better results we suggest building a custom library, depending on you usecase.

### Build a custom Database
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


# Comprehensive wet-bench and bioinformatics workflow for complex microbiota using Oxford Nanopore Technologies

In our published article "Comprehensive wet-bench and bioinformatics workflow for complex microbiota using Oxford Nanopore Technologies" in mSystems (2021) we present a comprehensive analysis pipeline with sampling, storage, DNA extraction, library preparation and bioinformatical evaluation for complex microbiomes sequenced with ONT (DOI:10.1128/mSystems.00750-21). 

This study consists of 6 different experiments. Here we provide download links for fastq-files and metadata (zipped together). During classification all fastq files will be merged/concatenated. To reorder the trimmed reads to their belonging samples we provide barcode.txt files for every experiment. With the following commands these files can be downloaded:

1. Swab finding
One stool sample was used to evaluate the reliability of different swabs (eSwab, eNAT, both  purchased from Copan) compared to direct DNA extraction (some stool was directly entered into the lysis buffer). All three kinds of collection methods were stored under different conditions: room temperature, -20° C, -80° C for 3 or 7 days or were directly extracted (day 0). 

Fastq-files and metadata:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/U7SJM6NlrZNgmkz/download"`
barcodes_swabfinding_16S:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/humpM6O2hJ1AWob/download"`

2. Daily profiles
5 people collected buccal swabs at 2 consecutive days examining the buccal microbiome alteration due to food intake and drinking a glass of water. The first swab was collected in the morning before breakfast (condition 1), the second 5 minutes after eating (condition 2), the third 30 minutes after eating (condition 3), the fourth 240 minutes after eating (condition 4), afterwards all participants drank 200ml water and again swabs were collected 5 minutes after drinking (condition 5), 30 minutes after drinking (condition 6) and 240 minutes after drinking (condition7).

Fastq-files and metadata:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/6aGux5csVk7nzpg/download"`
barcodes_dailyprofiles_16S: 
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/NTW7jDQCJV6QEew/download"`


3. Grade of stool
Rectal swabs from one individual were collected with 3 different grades of stool/contamination (0,+,++).

Fastq-files and metadata:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/tHQkhM4SkrDXTvi/download"`
barcodes_gradeofstool_metagenomics: 
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/RxVC2AgMabTl5yy/download"`

4. Alpha 16S rRNA
Buccal and rectal swabs were collected from one individual and DNA was extracted with 4 different DNA-extraction kits: MagMAX Microbiome Ultra Nucleic Acid Isolation Kit (Applied Biosystems), PureLink™ Microbiome DNA Purification Kit (Invitrogen), QIAmp DNA Investigator Kit (Qiagen) and QIAmp DNA Microbiome Kit (Qiagen). Two protocols were applied for all but the last kit: the original, according to manufacturers' protocol and a protocol modified according to International Human Microbiome Standard. The aim of this experiment was to detect the most reliable DNA extraction protocol for 16S rRNA ONT-sequences.  


Fastq-files and metadata:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/H4HIweMfZwPUdQc/download"`
barcodes_alpha_16S: 
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/II2ZNtg9R8F2Dfh/download"`

5. Alpha metagenomics
Buccal and rectal swabs were collected from one individual and DNA was extracted with 4 different DNA-extraction kits: MagMAX Microbiome Ultra Nucleic Acid Isolation Kit (Applied Biosystems), PureLink™ Microbiome DNA Purification Kit (Invitrogen), QIAmp DNA Investigator Kit (Qiagen) and QIAmp DNA Microbiome Kit (Qiagen). Two protocols were applied for all but the last kit: the original, according to manufacturers' protocol and a protocol modified according to International Human Microbiome Standard. The aim of this experiment was to detect the most reliable DNA extraction protocol for metagenomic ONT-sequences.


Fastq-files and metadata:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/yW2o3kAarT42j8Y/download"`
barcodes_alpha_metagenomics:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/5qxAlNX8nCTonvk/download"`

6. Mock community
A mock community was purchased from ZymoResearch (https://www.zymoresearch.de/collections/zymobiomics-microbial-community-standards/products/zymobiomics-gut-microbiome-standard) containing 15 bacterial species and 2 fungi. With this mock community Metapont was validated.   


Fastq-files:
` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/VprOlYE8ak232Ou/download"`

The simulated datasets used in the paper can be downloaded with:
- 10_taxa:  ` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/vfaBobqMOP6Zwkj/download"`
- Gut:      ` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/Delfe5tur3ke51Q/download"`
- Tumor:    ` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/2jRIHIHTGCkvLe4/download"`
- Metamaps: ` wget --content-disposition "https://owncloud.gwdg.de/index.php/s/bRI2vLSsnMXjwZ0/download"`

More datasets with corresponding metadata are publicly available in Qiita (study number: 13720).


