/*
 * Copyright GPL v2: 2016 By Dr Colin Kong
 * Wipe device or create file with random data
 */

#include <stdio.h>
#include <stdlib.h>

extern long mod();

main(argc, argv)
int argc;
char *argv[];
{
    FILE *fopen();
    FILE *fp_write;
    int i = 0;
    int meg = 0;
    int seed;

    if (argc == 3)
    {
        fp_write = fopen(argv[1], "wb");
        if (fp_write == NULL)
        {
            fprintf(stderr, "Error: Cannot open device or file: %s\n", argv[1]);
            exit(1);
        }

        seed = atoi(argv[2]);
        ran(seed);
        printf("Writing psendo random file %s with seed %d...\n", argv[1], seed);

        while (putc(ran(0), fp_write) != EOF)
        if (++i == 1048576)
        {
            printf("\r%d MB", ++meg);
            fflush(stdout);
            i = 0;
        }
        fclose(fp_write);
        printf("");
    }
    else
    {
        printf("\nwipe - Wipe device or create file with random data\n\n");
        printf("Usage: wipe /dev/device seed\n");
        printf("       wipe file seed\n");
    }
}

/* Uses 1 linear random number generator to produce integers */
int ran(seed)
int seed;
{
    long num1 = 7141;
    long inc1 = 54773;
    long mod1 = 259200;
    static long seed1;

    if (seed > 0)
    {
        seed1 = mod(seed+inc1, mod1);
        return(0);
    }
    else
    {
        seed1 = mod(num1*seed1+inc1, mod1);
        return(mod(seed1, 256));
    }
}

/* returns the remainder for integer division */
long mod(num1, num2)
long num1;
long num2;
{
    long temp = num1/num2;
    return(num1 - temp*num2);
}
