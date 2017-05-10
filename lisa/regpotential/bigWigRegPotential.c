#include "common.h"
#include "linefile.h"
#include "hash.h"
#include "localmem.h"
#include "options.h"
#include "verbose.h"
#include "basicBed.h"
#include "bigWig.h"
#include "bits.h"
#include <stdlib.h>
#include <math.h>


char *bedOut = NULL;
char *statsRa = NULL;
int sampleAroundCenter = 200000;
int decay = 10000;

/* void usage() */
/* /\* Explain usage and exit. *\/ */
/* { */
/* errAbort( */
/*   "bigWigRegPotential v2 - Compute bigWig RegPotential based on weight decay function\n" */
/*   "usage:\n" */
/*   "bigWigRegPotential -sampleAroundCenter=200000 in.bw hg38_refseq_TSS.bed out.tab \n " */
/*   "The output columns are:\n" */
/*   "   chr - chromosome \n" */
/*   "   start - gene TSS \n" */
/*   "   end - gene TSS + 1 \n" */
/*   "   name - refseq:gene_symbol\n " */
/*   "   score - weight decay * bigwig read count within range 100kb \n" */
/*   "Options:\n" */
/*   "   -decay=N - default 10kb, half weight decay distance, for promoter mark, turn to 1kb  \n" */
/*   "   -sampleAroundCenter=N - default 200kb (range 100kb), Take sample at region N bases wide centered around bed item, rather\n" */
/*   "                     than the usual sample in the bed item.\n" */
/*   ); */
/* } */

/* static struct optionSpec options[] = { */
/*    {"bedOut", OPTION_STRING}, */
/*    {"stats", OPTION_STRING}, */
/*    {"sampleAroundCenter", OPTION_INT}, */
/*    {"decay", OPTION_INT}, */
/*    {NULL, 0}, */
/* }; */

void checkUniqueNames(struct bed *bedList)
/* Make sure all names in bedList are unique */
{
struct hash *hash = hashNew(16);
struct bed *bed;
for (bed = bedList; bed != NULL; bed = bed->next)
    {
    char *name = bed->name;
    if (hashLookup(hash, name) != NULL)
        errAbort("%s duplicated in input bed", name);
    else
        hashAdd(hash, name, NULL);
    }
hashFree(&hash);
}

void hashChrsize(struct bed *bedList)
/* Make sure all names in bedList are unique */
{
struct hash *hash = hashNew(16);
struct bed *bed;
for (bed = bedList; bed != NULL; bed = bed->next)
    {
    char *name = bed->name;
    if (hashLookup(hash, name) != NULL)
        errAbort("%s duplicated in input bed", name);
    else
        hashAdd(hash, name, NULL);
    }
hashFree(&hash);
}

void addBigWigIntervalInfo(struct bbiFile *bbi, struct lm *lm, char *chrom, int start, int end,
			   int *pSumSize, int *pSumCoverage, double *pSumVal)
/* Read in interval from bigBed and add it sums. */
{
struct bbiInterval *iv, *ivList = bigWigIntervalQuery(bbi, chrom, start, end, lm);
*pSumSize += (end - start);
for (iv = ivList; iv != NULL; iv = iv->next)
    {
    int cov1 = rangeIntersection(iv->start, iv->end, start, end);
    if (cov1 > 0)
	{
	*pSumCoverage += cov1;
	*pSumVal += cov1 * iv->val;
	}
    }
}
	
int countBlocks(struct bed *bedList, int fieldCount)
/* Return the number of blocks in list, or if non-blocked beds, just number of beds. */
{
if (fieldCount < 12)
    return slCount(bedList);
int blockCount = 0;
struct bed *bed;
for (bed = bedList; bed != NULL; bed = bed->next)
    blockCount += bed->blockCount;
return blockCount;
}

void optionallyPrintBedPlus(FILE *f, struct bed *bed, int fieldCount, double extra)
/* Print BED to tab separated file plus an extra double-format column. */
{
if (f != NULL)
    {
    bedOutputN(bed, fieldCount, f, '\t', '\t');
    fprintf(f, "%g\n", extra);
    }
}

double sumSum;
long long sumCoverage;
long long sumSize;

void updateSums(double sum, int coverage, int size)
/* Just add to the above three numbers. */
{
sumSum += sum;
sumCoverage += coverage;
sumSize += size;
}

long long bbiTotalChromSize(struct bbiFile *bbi)
/* Return sum of sizes of all chromosomes */
{
struct bbiChromInfo *chrom, *chromList = bbiChromList(bbi);
long long total = 0;
for (chrom = chromList; chrom != NULL; chrom = chrom->next)
    total += chrom->size;
bbiChromInfoFreeList(&chromList);
return total;
}

long long bbiOneChromSize(char *chr, struct bbiChromInfo* chromList)
{
  struct bbiChromInfo *chrom;
  for (chrom = chromList; chrom != NULL; chrom = chrom->next)
    if (sameString(chrom->name, chr))
      return chrom->size;

  return 0;
}

/* Return all chromosomes in file.  Dispose of this with bbiChromInfoFreeList. */
void outputSums(char *fileName, struct bbiFile *bbi)
/* Write a little .ra file with results of sums. */
{
FILE *f = mustOpen(fileName, "w");
struct bbiSummaryElement sumEl = bbiTotalSummary(bbi);
double totalSignal = sumEl.sumData;
long long basesInGenome = bbiTotalChromSize(bbi);
fprintf(f, "spotRatio %g\n", sumSum/totalSignal);
fprintf(f, "enrichment %g\n", (sumSum/sumSize) / (totalSignal/basesInGenome));
fprintf(f, "maxEnrichment %g\n", (double)basesInGenome/sumSize);
fprintf(f, "basesInGenome %lld\n", basesInGenome);
fprintf(f, "basesInSpots %lld\n", sumSize);
fprintf(f, "basesInSpotsWithSignal %lld\n", sumCoverage);
fprintf(f, "sumSignal %g\n", totalSignal);
fprintf(f, "spotSumSignal %g\n", sumSum);
carefulClose(&f);
}


void averageFetchingEachBlock(struct bbiFile *bbi, struct bed *bedList, int fieldCount, 
	FILE *f, FILE *bedF)
/* Do the averaging fetching each block from bedList from bigWig.  Fastest for short bedList. */
{
struct lm *lm = lmInit(0);
struct bed *bed;
for (bed = bedList; bed != NULL; bed = bed->next)
    {
    int coverage = 0;
    double sum = 0.0;
    int size = 0;

    if (sampleAroundCenter > 0)
        {
	int center = (bed->chromStart + bed->chromEnd)/2;
	int left = center - (sampleAroundCenter/2);
	addBigWigIntervalInfo(bbi, lm, bed->chrom, left, left+sampleAroundCenter,
		&size, &coverage, &sum);
	}
    else
	{
	if (fieldCount < 12)
	    addBigWigIntervalInfo(bbi, lm, bed->chrom, bed->chromStart, bed->chromEnd, 
				  &size, &coverage, &sum);
	else
	    {
	    int i;
	    for (i=0; i<bed->blockCount; ++i)
		{
		int start = bed->chromStart + bed->chromStarts[i];
		int end = start + bed->blockSizes[i];
		addBigWigIntervalInfo(bbi, lm, bed->chrom, start, end, &size, &coverage, &sum);
		}
	    }
	}

    /* Print out result, fudging mean to 0 if no coverage at all. */
    double mean = 0;
    if (coverage > 0)
    	 mean = sum/coverage;

    fprintf(f, "%s\t%d\t%d\t%g\t%g\t%g\n", bed->name, size, coverage, sum, sum/size, mean);
    optionallyPrintBedPlus(bedF, bed, fieldCount, mean);
    updateSums(sum, coverage, size);
    }
}

int bedCmpChrom(const void *va, const void *vb)
/* Compare strings such as chromosome names that may have embedded numbers,
 * so that chr4 comes before chr14 */
{
const struct bed *a = *((struct bed **)va);
const struct bed *b = *((struct bed **)vb);
return cmpStringsWithEmbeddedNumbers(a->chrom, b->chrom);
}

struct bed *nextChromInList(struct bed *bedList)
/* Return first bed in list that starts with another chromosome, or NULL if none. */
{
char *chrom = bedList->chrom;
struct bed *bed;
for (bed = bedList->next; bed != NULL; bed = bed->next)
    if (!sameString(bed->chrom, chrom))
        break;
return bed;
}

void addBufIntervalInfo(double *valBuf, Bits *covBuf, int start, int center, int end,
			int *pSumSize, int *pSumCoverage, double *pSumVal, FILE *f, char *name, 
                        double *weights, char *chr, int leftExclude, int rightExclude)
/* Look at interval in buffers and add result to sums. */
{
/* int size1 = end - start; */
/* *pSumSize += size1; */
/* int cov1 = bitCountRange(covBuf, start, size1); */
/* *pSumCoverage += cov1; */
double sum1 = 0;
/* double weight = 0.0; */
/* double alpha = log(1.0/3.0)*10.0; */
int i, offset;
weights += sampleAroundCenter/2 + start - center;
if (leftExclude == rightExclude) {
for (i=start; i<=end; ++i) {
  /* weight = exp(alpha*fabs(i-center)/1e5); */
  /* weight = 2*weight/(1+weight); */
  sum1 += valBuf[i]*(*weights);
  weights++;
  /* printf("%d\n", i); */
}
} else {
for (i=start; i<=end; ++i) {
  offset = i-center;
  if (offset >= leftExclude && offset <= rightExclude) {
      weights++;
      continue;
  }
  sum1 += valBuf[i]*(*weights);
  weights++;
  /* printf("%d\n", i); */
}
}

fprintf(f, "%s\t%d\t%d\t%s\t%f\n", chr, center, center+1, name, sum1);
/* *pSumVal += sum1; */
}

void averageFetchingEachChrom(struct bbiFile *bbi, struct bed **pBedList, int fieldCount, 
	FILE *f, FILE *bedF, float d, int leftExclude, int rightExclude)
/* Do the averaging by sorting bedList by chromosome, and then processing each chromosome
 * at once. Faster for long bedLists. */
{
/* Sort by chromosome. */

slSort(pBedList, bedCmpChrom);

struct bigWigValsOnChrom *chromVals = bigWigValsOnChromNew();

struct bed *bed, *bedList, *nextChrom;

double *wp, *weights = (double *)malloc((sampleAroundCenter+1)*sizeof(double));
wp = weights;
double weight = 0.0;

decay = d;
double alpha;
if (decay>0)
	alpha = log(1.0/3.0)*(100000/decay);
else
	alpha = log(1.0/3.0)*10;

int i;
for (i=0; i<=sampleAroundCenter; ++i) {
  weight = exp(alpha*fabs(i-sampleAroundCenter/2)/1e5);
  weights[i] = 2*weight/(1+weight);
}

verbose(1, "processing chromosomes");

struct bbiChromInfo *chromList = bbiChromList(bbi);

for (bedList = *pBedList; bedList != NULL; bedList = nextChrom)
    {
    /* Figure out which chromosome we're working on, and the last bed using it. */
    char *chrom = bedList->chrom;

    // add chrom size here
    long long chrsize = bbiOneChromSize(chrom, chromList);

    /* verbose(1, "Processing %s\n", chrom); */
    /* verbose(1, "chr size: %lld\n", chrsize); */

    nextChrom = nextChromInList(bedList);
    /* verbose(2, "Processing %s\n", chrom); */

    if (chrsize > 0 && bigWigValsOnChromFetchData(chromVals, chrom, bbi))
	{
	double *valBuf = chromVals->valBuf;
	Bits *covBuf = chromVals->covBuf;

	/* Loop through beds doing sums and outputting. */
	for (bed = bedList; bed != nextChrom; bed = bed->next)
	    {
	    int size = 0, coverage = 0;
	    double sum = 0.0;
	    if (sampleAroundCenter > 0)
		{
//int center = (bed->chromStart + bed->chromEnd)/2;
                int center = bed->chromStart;
		int left = ((center - (sampleAroundCenter/2))>0)?(center - (sampleAroundCenter/2)):0;
                int right = (center + sampleAroundCenter/2 >=chrsize)?(chrsize):(center+sampleAroundCenter/2);
                /* printf("%d\t%d\t%d\n", left, center, right); */
                /* verbose(1, "marker\n"); */
		addBufIntervalInfo(valBuf, covBuf, left, center, right,
				   &size, &coverage, &sum, f, bed->name, wp, chrom, leftExclude, rightExclude);
		}
//	    else
//		{
//		if (fieldCount < 12)
//		    {
//                      addBufIntervalInfo(valBuf, covBuf, bed->chromStart, (bed->chromStart+bed->chromEnd)/2, bed->chromEnd,
//                                         &size, &coverage, &sum, f, bed->name, wp, chrom);
//		    }
//		else
//		    {
//		    int i;
//		    for (i=0; i<bed->blockCount; ++i)
//			{
//			int start = bed->chromStart + bed->chromStarts[i];
//			int end = start + bed->blockSizes[i];
//			addBufIntervalInfo(valBuf, covBuf, start, (start+end)/2, end, &size, &coverage, &sum, f, bed->name, wp, chrom);
//			}
//		    }
//		}
//
	    /* Print out result, fudging mean to 0 if no coverage at all. */
	    /* double mean = 0; */
	    /* if (coverage > 0) */
	    /* 	 mean = sum/coverage; */
	    /* fprintf(f, "%s\t%d\t%d\t%g\t%g\t%g\n", bed->name, size, coverage, sum, sum/size, mean); */
	    /* optionallyPrintBedPlus(bedF, bed, fieldCount, mean); */
	    /* updateSums(sum, coverage, size); */
	    }
	verboseDot();
	}
    else
        {
	/* If no bigWig data on this chromosome, just output as if coverage is 0 */
	for (bed = bedList; bed != nextChrom; bed = bed->next)
	    {
	    /* fprintf(f, "%s\t%d\t0\t0\t0\t0\n", bed->name, bedTotalBlockSize(bed)); */
        fprintf(f, "%s\t%d\t%d\t%s\t0\n", chrom, bed->chromStart, bed->chromStart+1, bed->name);
            //fprintf(f, "%s\t0\n", bed->name);
	    /* optionallyPrintBedPlus(bedF, bed, fieldCount, 0); */
	    }
	}
    }
bigWigValsOnChromFree(&chromVals);
bbiChromInfoFreeList(&chromList);
free(weights);
verbose(1, "\n");
}

void bigWigAverageOverBed(char *inBw, char *inBed, char *outTab, float alpha, int left, int right)
/* bigWigAverageOverBed - Compute average score of big wig over each bed, which may have introns. */
{
struct bed *bedList;
int fieldCount;
bedLoadAllReturnFieldCount(inBed, &bedList, &fieldCount);
// checkUniqueNames(bedList);
struct bbiFile *bbi = bigWigFileOpen(inBw);
FILE *f = fopen(outTab, "w");
FILE *bedF = NULL;
if (bedOut != NULL)
    bedF = mustOpen(bedOut, "w");
/* Count up number of blocks in file.  It takes about 1/100th of of second to
 * look up a single block in a bigWig.  On the other hand to stream through
 * the whole file setting a array of doubles takes about 30 seconds, so we change
 * strategy at 3,000 blocks. 
 *   I (Jim) usually avoid having two paths through the code like this, and am tempted
 * to always go the ~30 second chromosome-at-a-time  way.  On the other hand the block-way
 * was developed first, and it was useful to have both ways to test against each other.
 * (This found a bug where the chromosome way wasn't handling beds in chromosomes not
 * covered by the bigWig for instance).  Since this code is not likely to change too
 * much, keeping both implementations in seems reasonable. */
// int blockCount = countBlocks(bedList, fieldCount);
// verbose(2, "Got %d blocks, if >= 3000 will use chromosome-at-a-time method\n", blockCount);

//if (blockCount < 3000)
//    averageFetchingEachBlock(bbi, bedList, fieldCount, f, bedF);
//else
averageFetchingEachChrom(bbi, &bedList, fieldCount, f, bedF, alpha, left, right);
bbiFileClose(bbi);
fclose(f);
if (statsRa != NULL)
    outputSums(statsRa, bbi);
carefulClose(&bedF);
}

/* int main(int argc, char *argv[]) */
/* /\* Process command line. *\/ */
/* { */
/* optionInit(&argc, argv, options); */
/* if (argc != 4) */
/*     usage(); */
/* bedOut = optionVal("bedOut", bedOut); */
/* statsRa = optionVal("stats", statsRa); */
/* decay = optionInt("decay", decay); */
/* sampleAroundCenter = optionInt("sampleAroundCenter", sampleAroundCenter); */
/* bigWigAverageOverBed(argv[1], argv[2], argv[3]); */
/* return 0; */
/* } */
