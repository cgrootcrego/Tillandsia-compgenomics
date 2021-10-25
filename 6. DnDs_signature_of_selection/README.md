# Inferring signatures of selection by calculating dN/dS ratios between T. fasciulata and T. leiboldiana

In this section, we infer dN / dS ratios for all single-copy pairs of orthologous genes between T. fasciculata and T. leiboldiana. Part of this work was done by Francesca Beclin. We obtained Dn / Ds ratios by aligning the orthologous sequences using a codon-aware aligner (MACSE) and inferring ratios with KaKs_Calculator and PAML.

# Selecting single-copy orthogroups and compiling per-orthogroup fastafiles

First I compiled the sequences of each gene into per-orthogroup fastafiles. For this, I extracted the one-to-one genes obtained in orthofinder analyses from the annotation gff files of each assembly. The orthofinder file used for this was: /scratch/grootcrego/orthofinder/run_orthofinder_Tfas_Tlei_Acom_25_scaffolds/OrthoFinder/Results_Jan22/Phylogenetic_Hierarchical_Orthogroups/one-to-one_orthogroups_Tfas_Tlei.txt and was created in the postprocessing of orthofinder results (see Orthology&Synteny notes). There are 13,128 orthologous pairs in this file.

To extract the features belonging only to one-one orthologous genes:

    grep -f one-to-one_orthogroups_Tfas_Tlei.IDonly.txt \
    Tillandsia_fasciculata_v1.2.edited_allfeatures.gff > \
    Tillandsia_fasciculata_v1.2.edited_allfeatures.one-to-one_orthologs.gff

Then I extracted the coding sequence features and replaced ID with Name to make the below python script work:

    awk '$3 == "CDS" {print $0}' [gff] > [gff.CDSonly]
    sed 's/ID=/Name=/g' [gff.CDSonly] > [gff.CDSonly2]

I then modified the scaffold names in the gff file from the old system ("scaffold_8339") to a new system ("chr1"):

    cat chrnames_Tfas.txt | while read line ;
    do
     Name=`echo "$line"|awk '{print $1}'`;
     echo $Name;
     Replace=`echo "$line"|awk '{print $2}'`;
     echo $Replace;
     sed  -i "s/$Name/$Replace/g" Tillandsia_fasciculata_v1.2.one-to-one_orthologs.CDSonly.gff;
    done

Then I extracted the fasta sequences for each orthologue and species using with `script_CutSeq_modified.py`, which is a modified form of one of Tibo's scripts to include a more informative header:

    while read line; do python2 cutSeqGff_mod.py  \
    Tfas_assembly/per_chrom_fasta/Tfas_$line.fasta \
    Tillandsia_fasciculata_v1.2.one-to-one_orthologs.CDSonly.gff \
    $line CDS; done < chr_Tfas.txt

I also compiled a list of orthologous gene pairs per orthogroup, which is used to compile the fasta sequences. This was done with the python script `script_compile_per-orthogroup_gene_list.py`

Then I used the following bash script and the resulting file to compile orthologous fasta sequences into one fasta file:

    cat ../one-to-one_orthogroups_Tfas_Tlei.perOG.txt | while read line ;
    do
     Orthogroup=`echo "$line"|awk '{print $1}'`;
     echo $Name;
     Tfas=`echo "$line"|awk '{print $2}'`;
     Tlei=`echo "$line"|awk '{print $3}'`;
     cat ../Tfas_seq/$Tfas:cds.fst ../Tlei_seq/$Tlei:cds.fst > $Orthogroup.fasta
    done

# Checking for completeness and length differences between orthologous pairs

Since Dn/Ds ratios are very sensitive to alignment quality, we first wanted to have an idea of the completeness of our gene pairs (i.e. presence of a start and stop codon) and their lengths. I therefore made a "checklist" containing this information for each gene using the script `script_make_checklist_completeness_length_orthologous_genes.py`
This file was eventually modified in R to a per-orthogroup format in which the absolute difference in sequence length between pairs was calculated. Additionally, Francesca calculated relative differences for each species (diff/length_Tfas and diff/length_Tlei) and noted completeness in the orthogroup (both complete / one complete / zero complete). Additionally, francesca counted the exon number per gene and the difference in counts between genes.

# Testing filtering options of alignments based on length differences and completeness

We created four subsets with different degrees of filtering to run preliminary dN/dS analyses on:

- stringent filtering: both alignments are complete (they have a start and stop codon), they have an absolute length difference of maximum 200 basepairs and they have a relative length difference that is smaller than 0.1 (meaning that the difference in length is no more than 10 % of the total length of that gene).
- relaxed completeness: same requirements as above regarding length differences, but only one gene is complete.
- relaxed relative difference: both genes have to be complete and the same requirement applies for absolute length differences as above. However, the relative length difference ranges from 0.1 to 0.2.
- relaxed completeness and relative difference: absolute length requirement remains the same, but relative differences range from 0.1 to 0.2 and only one gene is complete.

The total number of orthogroups for each subset was:
6208  stringent filtering (47 %)
493   relaxed relative difference (4 %)
2569  relaxed completeness (19 %)
316   relaxed relative difference and completeness (2 %)

Francesca then randomly selected 200 orthogroups for each filtering setting and performed alignments with them.

Alignments on subsets were performed twice, once with very basic code and once with more specific requirements that optimize the alignment:

    # Basic alignment
    for i in *; do
     java -jar macse_v2.05.jar -prog alignSequences -seq $i ;
    done
    # Extensive alignment
    for i in *; do
     java -jar macse_v2.05.jar -prog alignSequences -seq $i -local_realign_init 1 -local_realign_dec 1 ;
    done

The alignments were then converted into .axt files using a modified form of the script
03_ConvertFasta.py from the {AlignmentProcessor}(https://github.com/WilsonSayresLab/AlignmentProcessor/blob/master/bin/03_ConvertFasta.py) software. Preliminary dN/dS ratios were then calculated with KaKs calculator and the MYN model using a modified script of 04_CallKaKs.py from ALignmentProcessor.

Comparing the distribution of dN/dS ratios between filtering categories showed that relaxing length difference didn't cause extreme values of dN/dS. However, relaxing completeness did cause a few estimates to show up, though most estimates were still in the same range as with stringent filtering. I therefore decided to keep the filtering loose at this point, and only remove alignments of genes where both are incomplete and where length differences are > 0.2 in both genes. This kept 10,362 orthologous pairs for pairwise alignment, which is almost 80 % of the original set.

# Calculating pairwise dN / dS ratios for the final dataset

Next, using the checklist, I selected all genes:

	grep -v "0 complete" checklist_with_diff_completeness.txt | \
	awk '$5 > -0.2 && $5 < 0.2 && $6 > -0.2 && $6 < 0.2' | cut -f 1 | \
	sed 's/"//g' > orthogroups_final_subset_0.2_lengthdiff_1_complete.txt

Alignment was done with optimization parameters for all orthologous pairs with the bash script `run_macse.sh`.

As CodeML allows for pairwise calculation of dN / dS values, I decided to drop KaKsCalculator and find a way to automate CodeML. I discovered the {ETE toolkit}(http://etetoolkit.org/documentation/ete-evol/), which allows such a thing.

# Calculating branch-specific dN /dS ratios in CodeML using an outgroup