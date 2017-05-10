
int bigWigSummary(char *bigWigFile, char *chrom, int start, int end, int dataPoints, double *summaryValues, char *summaryType);

//void bigWigAverageOverBed(char *inBw, char *inBed, char *outTab, float d);

void bigWigAverageOverBed(char *inBw, char *inBed, char *outTab, float alpha, int left, int right);
