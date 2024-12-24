/*
 * API.h
 *
 *  Created on: Feb 23, 2023
 *      Author: gene
 */

#include <stdint.h>
#include "comp.h"

#ifndef SRC_API_H_
#define SRC_API_H_

int initialize(int Fs, int Rs, int M, int P, int Nsym, int f1_tx, int tone_spacing,int *sizeOfbitbuf, int *sizeOfmodbuf);
int demod();
int getNin();

#endif /* SRC_API_H_ */
