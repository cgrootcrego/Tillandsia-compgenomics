#!/usr/bin/env python
import sys

genes = open(sys.argv[1])
outputfilename=sys.argv[1].replace(".txt",".categories.txt")
output1=open(outputfilename,'w')
equal = 0
acom_more = 0
tfas_more = 0
tlei_more = 0
tillandsia_more = 0
variable = 0
orthogroups = list()
for line1 in genes.readlines():
    line1 = line1.replace('\n','')
    splitted_line1 = line1.split('\t')
    acom_count = splitted_line1[7]
    tfas_count = splitted_line1[8]
    tlei_count = splitted_line1[9]
    orthog = splitted_line1[6]

    if acom_count == tfas_count and acom_count == tlei_count:
        new_line = line1+"\tequal\n"
        output1.write(new_line)
        if orthog not in orthogroups:
            equal = equal + 1
            orthogroups.append(orthog)
    elif acom_count > tfas_count and tfas_count == tlei_count:
        new_line = line1+"\tacom_more\n"
        output1.write(new_line)
        if orthog not in orthogroups:
            acom_more = acom_more + 1
            orthogroups.append(orthog)
    elif acom_count < tfas_count and tfas_count == tlei_count:
        new_line = line1+"\ttillandsia_more\n"
        output1.write(new_line)
        if orthog not in orthogroups:
            tillandsia_more = tillandsia_more + 1
            orthogroups.append(orthog)
    elif acom_count < tfas_count and acom_count == tlei_count:
        new_line = line1+"\ttfas_more\n"
        output1.write(new_line)
        if orthog not in orthogroups:
            tfas_more = tfas_more + 1
            orthogroups.append(orthog)
    elif acom_count < tlei_count and acom_count == tfas_count:
        new_line = line1+"\ttlei_more\n"
        output1.write(new_line)
        if orthog not in orthogroups:
            tlei_more = tlei_more + 1
            orthogroups.append(orthog)
    else:
        new_line = line1+"\tvariable\n"
        output1.write(new_line)
        if orthog not in orthogroups:
            variable = variable + 1
            orthogroups.append(orthog)

stats_to_print = "Types of CNV changes:\nNr. gene families that remained equal: {}\nNr. gene families larger in A.comosus: {}\nNr. gene families larger in Tillandsia: {}\nNr. gene families larger in T. fasciculata: {}\nNr. gene families larger in T. leiboldiana: {}\nNr. gene families with changes in more than one species: {}".format(equal, acom_more, tillandsia_more, tfas_more, tlei_more, variable)
print(stats_to_print)
