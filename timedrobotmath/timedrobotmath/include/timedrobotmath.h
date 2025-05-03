
#pragma once

int getSizeOfLong();

long cppCalcFutureExpirationUs(
    long expirationTimeUs,
    long offsetUs,
    long periodUs,
    long currentTimeUs);

