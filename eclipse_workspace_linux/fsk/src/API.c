/*
 * API.c
 *
 *  Created on: Feb 23, 2023
 *      Author: gene
 */
#include <assert.h>
#include "API.h"
#include "fsk.h"

static struct FSK *fsk;
static uint8_t *bitbuf = NULL;
static COMP *modbuf    = NULL;
static int fsk_lower = 0;
static int fsk_upper = 0;
static int mask = 0;

int initialize(int Fs, int Rs, int M, int P, int Nsym, int f1_tx, int tone_spacing,int *sizeOfbitbuf, int *sizeOfmodbuf)
{
	int rtn = 1;

    /* set up FSK */
    fsk = fsk_create_hbr(Fs,Rs,M,P,Nsym,f1_tx,tone_spacing);

	fsk_lower = -Fs/2;
	fsk_upper = Fs/2;
	fsk_set_freq_est_limits(fsk,fsk_lower,fsk_upper);
    fsk_set_freq_est_alg(fsk, mask);

    *sizeOfbitbuf = sizeof(uint8_t)*fsk->Nbits;
    *sizeOfmodbuf = sizeof(COMP)*(fsk->N+fsk->Ts*2);

    bitbuf = (uint8_t*)malloc(*sizeOfbitbuf); assert(bitbuf != NULL);
    modbuf = (COMP*)malloc(*sizeOfmodbuf);

	return rtn;
}

int getNin()
{
	return fsk->nin;
}


int demod(uint8_t rx_bits[], COMP fsk_in[])
{
	int rtn = 1;

	//printf("API point 1\n");
	fsk_demod(fsk,rx_bits,fsk_in);
	//printf("%f\n",fsk->SNRest);

	return rtn;
}


int getSNR()
{
	//printf("%f\n",fsk->SNRest);

	return fsk->SNRest;
}
