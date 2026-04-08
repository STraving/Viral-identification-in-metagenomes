# Viral-identification-in-metagenomes
Pipeline for the identification of viral sequences in metagenomic data using VirSorter2, with subsequent quality check using CheckV and DRAMv.
Dependencies:

  VirSorter2 (v.) https://github.com/jiarong/VirSorter2
  
  CheckV (v.) https://doi.org/10.1038/s41587-020-00774-7
  
  DRAMv (v.) https://github.com/WrightonLabCSU/DRAM

  vRhyme (v.) https://github.com/AnantharamanLab/vRhyme

  The following cutoffs and choices are curated for the metagenomic data used in HADAL - Danish Center for Hadal Research at the University of Southern Denmark.

#Identify viral sequences in the assembly.

The cutoff length is set to 5000, as that is the minimum size required downstream.

    virsorter run --keep-original-seq -i assembly_contigs.fa -w vs2-pass1/Complete_contigs --include-groups dsDNAphage,NCLDV,RNA,ssDNA,lavidaviridae --min-length 5000 --min-score 0.5 -j 32 all
