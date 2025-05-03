
#include "timedrobotmath.h"


int getSizeOfLong() {
    return sizeof(long);
}

long cppCalcFutureExpirationUs(
    long expirationTimeUs,
    long offsetUs,
    long periodUs,
    long currentTimeUs) {

    return expirationTimeUs + offsetUs + periodUs + (currentTimeUs-expirationTimeUs) / periodUs * periodUs;
}

