# Viral bioinformatics pipeline for HADAL
  The following steps and choices are curated for the metagenomic datasets produced in HADAL - Danish Center for Hadal Research at the University of Southern Denmark.
  This is also designed with a "global" approach in mind, analysing datasets from multiple trenches, and at the same time process the data in a way that (hopefully)
  will be the most efficient and flexible for future needs, e.g. different combinations of samples and datasets across all.

### Within trench pipeline:
viral identification (Virsorter2)
QC (CheckV)
viral prep (VirSorter2)
merge sequences (final-viral-contigs.fa fpr each sample)
dereplication (BBMap) - permanent save of dereplicated sequences
annotation (DRAMv) - permanent save of annotation table
vOTUs: 95% ANI clustering (skani) - permanent save complete cluster-member list
relative abundance on vOTUs (metaBAT and samtools)
network analysis on vOTUs (vCONTACT3)
virus-host prediction (VHIP)

### Multi-trench pipeline:
merge vOTUs for the target trenches/datasets
dereplicate (BBmap)
vOTUs: 95% ANI clustering (skani)
network analysis on vOTUs (vCONTACT3)
virus-host prediction (VHIP)

## Preperation work
Some initial housekeeping work is often required to manage sample names and ensuring unique identifiers in different constellations.
NOTE: before running the rename_assemblies.py script ensure the right path is given to the folder containing the assemblies and the output folder for the renamed ones.
Also check that you have all the sample names included in the "translation" key in the script.

    python3 rename_assemblies.py

The script will tell you if there are samples which did not get their headers renamed.

Now we changed the headers from something like "Complete_Site_1_Depth_0_0000000001" to "AT01D00_c0000000001" thats a more manageable sample ID string which we can carry on with in all the intended downstream purposes.


## Viral-identification-in-metagenomes
Pipeline for the identification of viral sequences in metagenomic data using VirSorter2, with subsequent quality check using CheckV and DRAMv.
Dependencies:

  VirSorter2 (v.) https://github.com/jiarong/VirSorter2
  
  CheckV (v.) https://doi.org/10.1038/s41587-020-00774-7
  
  DRAMv (v.) https://github.com/WrightonLabCSU/DRAM

  vRhyme (v.) https://github.com/AnantharamanLab/vRhyme


#Identify viral sequences in the assembly.

The cutoff length is set to 5000, as that is the minimum size required downstream.

    virsorter run --keep-original-seq -i assembly_contigs.fa -w vs2-pass1/Complete_contigs --include-groups dsDNAphage,NCLDV,RNA,ssDNA,lavidaviridae --min-length 5000 --min-score 0.5 -j 32 all

Quality check

    checkv end_to_end ~/vs2-pass1/Complete_contigs/final-viral_combined.fa ~/checkv1/ -t 32 -d /work/software/sachia_env/viral-id-sop/checkv-db-v1.0

Combine prophages and phages

    cat proviruses.fna viruses.fna > combined.fna

Run Virsorter2 again this time to prep files for DRAMv

    virsorter run --seqname-suffix-off --viral-gene-enrich-off --prep-for-dramv -i ~/combined.fna -w ~/vs2-pass2/ --include-groups dsDNAphage,ssDNA,RNA,NCLDV,lavidaviridae --min-length 5000 --min-score 0.5 -j 32 all


## Merging samples
Depending on the scope of the research question the appropriate samples are merged before downstream analyses. The default is to merge at the trench level.


## Dereplication

BBMap - remove identical sequences

## Annotation 

    DRAM-v.py annotate -i ~/vs2-pass2/for-dramv/final-viral-combined-for-dramv.fa -v ~/vs2-pass2/for-dramv/viral-affi-contigs-for-dramv.tab -o dramv-annotate --skip_trnascan --threads

    
Re-order sequences to ensure the best representative sequence is chosen in the clustering
  checkv score
  sequence length
  circular over linear

## Clustering
using Skani to create vOTUs
the "--write-cluster" will save all the members of the cluster.

    skani cluster -i input.fna -o out_dir --min-ani 0.95 --min-aln-fraction 0.85 --write-clusters
    

## Relative abundance
this is chosen to do at the vOTU level.


# Multi-trench studies
We merge the (merged and dereplicated) datasets from each trench and dereplicate again across trenches.



    DRAM-v.py annotate -i ~/vs2-pass2/for-dramv/final-viral-combined-for-dramv.fa -v ~/vs2-pass2/for-dramv/viral-affi-contigs-for-dramv.tab -o dramv-annotate --skip_trnascan --threads

## Relative abundance

## Viral network
