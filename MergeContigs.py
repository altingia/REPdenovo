__author__ = 'Chong Chu'

import sys
import os
from subprocess import *
from Utility import printCommand
from Utility import BWA_PATH
from Utility import getBWAPath
from Utility import SAMTOOLS_PATH
from Utility import getSamtoolsPath
from Utility import REFINER_PATH
from Utility import getRefinerPath

def removeDuplicateContained(fcontig, foutput, cutoff, brm_contained):
    BWA_PATH=getBWAPath()
    SAMTOOLS_PATH=getSamtoolsPath()
    REFINER_PATH=getRefinerPath()

    #remove duplicate or contained contigs
    cmd="{0} faidx {1}".format(SAMTOOLS_PATH,fcontig)
    printCommand("Running command: "+cmd)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="{0} -U -r {1} -o {2}".format(REFINER_PATH,fcontig,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    cmd="{0} faidx {1}".format(SAMTOOLS_PATH,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="{0} index {1}".format(BWA_PATH,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="{0} mem -a {1} {2} > {3}.itself.sam".format(BWA_PATH,fcontig,fcontig,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    cmd="{0} view -h -S -b {1}.itself.sam > {2}.itself.bam".format(SAMTOOLS_PATH,fcontig,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="{0} sort {1}.itself.bam {2}.itself.sort".format(SAMTOOLS_PATH,fcontig,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="{0} index {1}.itself.sort.bam".format(SAMTOOLS_PATH,fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    if brm_contained==True:
        cmd="{0} -P -b {1}.itself.sort.bam -r {2} -o {3} -c {4} -g".format(REFINER_PATH,fcontig,fcontig,foutput,cutoff)
    else:
        cmd="{0} -P -b {1}.itself.sort.bam -r {2} -o {3} -c {4}".format(REFINER_PATH,fcontig,fcontig,foutput,cutoff)
    printCommand(cmd)
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    ##clean all the temporary files
    cmd="rm {0}.sa".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.pac".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.bwt".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.ann".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.amb".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.itself.sam".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.itself.bam".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.itself.sort.bam".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.itself.sort.bam.bai".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    cmd="rm {0}.fai".format(fcontig)
    Popen(cmd, shell = True, stdout = PIPE).communicate()


def mergeContigs(contigs_merger_path, fout_folder, nthreads, cutoff_dup_bf_merge, cutoff_dup_af_merge):
    fcontig=fout_folder+"contigs.fa"
    foutput=fcontig+"_no_dup.fa"
    removeDuplicateContained(fcontig, foutput, cutoff_dup_bf_merge, False)

    cmd="{0} -s 0.2 -i1 -6.0 -i2 -6.0 -x 15 -k 10 -t {1} -m 1 -o {2}.merge.info {3} > {4}.merged.fa".format(contigs_merger_path,nthreads,foutput,foutput,foutput)
    printCommand(cmd)
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    fcontig="{0}.merged.fa".format(foutput)
    foutput="{0}.no_dup.fa".format(fcontig)
    removeDuplicateContained(fcontig,foutput, cutoff_dup_af_merge, False)
    fcontig=foutput
    foutput=fcontig+".no_contained.fa"
    removeDuplicateContained(fcontig, foutput, cutoff_dup_af_merge, True)

    #rename contigs.fa
    os.rename(fout_folder+"contigs.fa", fout_folder+"original_contigs_before_merging.fa")
    os.rename(foutput,fout_folder+"contigs.fa")

