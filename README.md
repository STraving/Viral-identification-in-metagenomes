# Viral bioinformatics pipeline for HADAL
by Sachia J. Traving, University of Southern Denmark and University of Copenhagen

  The following steps and choices are curated for the metagenomic datasets produced in HADAL - Danish Center for Hadal Research at the University of Southern Denmark.
  This is also designed with a "global" approach in mind, analysing datasets from multiple trenches, and at the same time process the data in a way that (hopefully)
  will be the most efficient and flexible for future needs, e.g. different combinations of samples and datasets across all.

### Within trench pipeline:
1. viral identification (Virsorter2)
2. QC (CheckV)
3. viral prep (VirSorter2)
4. merge sequences (final-viral-contigs.fa for each sample)
5. dereplication (BBMap) - permanent save of dereplicated sequences
6. annotation (DRAMv) - permanent save of annotation table
7. vOTUs: 95% ANI clustering (skani) - permanent save complete cluster-member list
8. relative abundance on vOTUs (metaBAT and samtools)
9. network analysis on vOTUs (vCONTACT3)
10. virus-host prediction (VHIP)

### Multi-trench pipeline:
- merge vOTUs for the target trenches/datasets
- dereplicate (BBmap)
- vOTUs: 95% ANI clustering (skani)
- network analysis on vOTUs (vCONTACT3)
- virus-host prediction (VHIP)

## Installation

For installing the required tools I would like to draw attention to protocol by Jiarong Guo and the Sullivan Lab (https://dx.doi.org/10.17504/protocols.io.btv8nn9w), I think they did a great job explaining things and the most common challenges in setting up the tools. Do notice that after step 4 is where this guide diverge from this protocol. 

## Preparation work

Some initial housekeeping work is often required to manage sample names and ensuring unique identifiers in different constellations. This is particular for HADAL samples but it is worth to pay attention to if you are from outside HADAL.
NOTE: before running the rename_assemblies.py script ensure the right path is given to the folder containing the assemblies and the output folder for the renamed ones.
Also check that you have all the sample names included in the "translation" key in the script.

    python3 rename_assemblies.py

The script will tell you if there are samples which did not get their headers renamed.

Now we changed the headers from something like "Complete_Site_1_Depth_0_0000000001" to "AT01D00_c0000000001" thats a more manageable sample ID string which we can carry on with in all the intended downstream purposes.


## Viral identification in metagenomes
Pipeline for the identification of viral sequences in metagenomic data using VirSorter2, with subsequent quality check using CheckV and DRAMv.
Dependencies:

  VirSorter2 (v.) https://github.com/jiarong/VirSorter2
  
  CheckV (v.) https://doi.org/10.1038/s41587-020-00774-7
  
  DRAMv (v.) https://github.com/WrightonLabCSU/DRAM

  vRhyme (v.) https://github.com/AnantharamanLab/vRhyme


### 1. Viral identification

We are using VirSorter2 by Guo et al., 2021 (https://doi.org/10.1186/s40168-020-00990-y).

    virsorter run --keep-original-seq -i assembly_contigs.fa -w vs2-pass1/Complete_contigs --include-groups dsDNAphage,NCLDV,RNA,ssDNA,lavidaviridae --min-length 5000 --min-score 0.5 -j 32 all

The cutoff length is set to 5000, as that is the minimum size required downstream.

### 2. Quality check

We are using CheckV by Nayfach et al., 2021 (https://doi.org/10.1038/s41587-020-00774-7)

    checkv end_to_end ~/vs2-pass1/Complete_contigs/final-viral_combined.fa ~/checkv1/ -t 32 -d /work/software/sachia_env/viral-id-sop/checkv-db-v1.0

### Merge prophages with phages
CheckV will keep phages identified as prophages in a separate file. Since one of our main focus areas in HADAL is auxiliary metabolic genes (AMGs) we are interested in including prophages.

    cat proviruses.fna viruses.fna > combined.fna

### 4. Prepare contigs for DRAMv

    virsorter run --seqname-suffix-off --viral-gene-enrich-off --prep-for-dramv -i ~/combined.fna -w ~/vs2-pass2/ --include-groups dsDNAphage,ssDNA,RNA,NCLDV,lavidaviridae --min-length 5000 --min-score 0.5 -j 32 all

### 5. Merge samples
Up until this stage, individual samples or metagenomes have been processed individually. This is to keep file sizes manageable and it gives us flexibility for subsetting samples and data across our different collections, without having to repeat the same analyses every time. 
This is the stage where, depending on the scope of the research question, the appropriate samples are merged before downstream analyses. The default is to merge at the trench level.

### 5. Dereplication
Weremove duplicate sequences using the dedupe.sh function in BBmap by Bushnell https://github.com/BioInfoTools/BBMap/tree/master?tab=readme-ov-file
      
    dedupe.sh combined-for-dramv.fna combined-for-dramv-deduped.fna

### 6. Annotation 

Next we want to annotate the viral contigs using DRAMv by Schaffer et al., 2020 (https://doi.org/10.1093/nar/gkaa621)
We want to do this before clustering, to ensure we don't overlook AMGs in viruses merged during the clustering process.

    DRAM-v.py annotate -i ~/vs2-pass2/for-dramv/final-viral-combined-for-dramv.fa -v ~/vs2-pass2/for-dramv/viral-affi-contigs-for-dramv.tab -o dramv-annotate --skip_trnascan --threads 32

Depending on file size it might run smoother by splitting up the dereplicated contig file into subsets and merge the DRAMv output afterwards. 
    
Re-order sequences to ensure the best representative sequence is chosen in the clustering
 
  - checkv score
  - sequence length
  - circular over linear

### 7. Clustering
Creating vOTUs using Skani by Shaw and Yu, 2023 (https://doi.org/10.1038/s41592-023-02018-3)

Clustering is done on the dereplicated contig file, so the output file created in step 5.

Note: the "--write-cluster" will save all the members of the cluster.

    skani cluster -i combined-for-dramv-deduped.fna -o out_dir --min-ani 0.95 --min-aln-fraction 0.85 --write-clusters

IMPORTANT: Save the cluster member list, this is your key to connect the information on the original viral contigs, AMGs, and relative abundance to the vOTUs.  

### 8. Relative abundance
this is chosen to do at the vOTU level. We map raw reads onto the representative contigs to calculate a coverage value used as a proxy for abundance.
We follow the steps which also is outlined in the documentation from a metagenomics summer course by a group of people at Aucklund University, here: https://genomicsaotearoa.github.io/metagenomics_summer_school/day3/ex14_gene_annotation_part2/#calculating-per-sample-coverage-stats-for-prokaryotic-bins

We use Bowtie2 by Langmead and Salzberg, 2013 (https://doi.org/10.1038/nmeth.1923) and samtools by 

First we index the vOTU representative contigs using Bowtie2

    conda activate bowtie2
    bowtie2-build vOTU-contigs.fa output_dir

We use Samtools to sort

    samtools sort input.sam -o output.bam

To normalize the coverage values so we can compare between samples we use MetaBAT by Kang et al., 2015 (https://doi.org/10.7717/peerj.1165) 

    conda activate metaBAT
    jgi_summarize_bam_contig_depths --outputDepth outputfilename.txt /file/path/to/.bam

### 9. Network analysis

We use vCONTACT3 by Buldoc et al., 2025 (preprint: doi: https://doi.org/10.1101/2025.11.06.686974)




### 10. Virus-host predictions

This is a fairly newer set of tools being developed trying to predict virus-host relationships from metagenomic data.

Right now we are testing out the tool VHIP by Bastien et al., 2024 (https://doi.org/10.1371/journal.pcbi.1011649)

The steps for producing the prokaryotic bins (MAGs) are not described here. we might add the information at a later stage.


# Multi-collection studies

We merge the datasets from the collections of interest.
There are some different options to choose.

1. Merge dereplicated contigs, dereplicate again, followed by clustering and abundance calculations on vOTU reps.
2. merge vOTU collection, dereplicate, cluster again and source abundance values from step 7 to calculate new average abundances.
3. merge vOTU collection, dereplicate, abundance calculations on combined vOTU collection reps.




## Relative abundance

if the multi-collection data is merged on the vOTU level then the abundance data can be sourced back from the initial sample processing (step 7). using the 
## Viral network
