from .common.BuiltIn import *
from .common.Uint import *

'''
    @dev Compute the nearest integer to the quotient of `n / d`
'''
def roundDiv(n, d):
    return n // d + (n % d) // (d - d // 2);

'''
    @dev Compute the largest integer smaller than or equal to the binary logarithm of `n`
'''
def floorLog2(n):
    res = 0;

    if (n < 256):
        # at most 8 iterations
        while (n > 1):
            n >>= 1;
            res += 1;
    else:
        # exactly 8 iterations
        for s in [1 << (8 - 1 - k) for k in range(8)]:
            if (n >= 1 << s):
                n >>= s;
                res |= s;

    return res;

'''
    @dev Compute the largest integer smaller than or equal to the square root of `n`
'''
def floorSqrt(n):
    if (n > 0):
        x = n // 2 + 1;
        y = (x + n // x) // 2;
        while (x > y):
            x = y;
            y = (x + n // x) // 2;
        return x;
    return 0;

'''
    @dev Compute the smallest integer larger than or equal to the square root of `n`
'''
def ceilSqrt(n):
    x = floorSqrt(n);
    return x if x * x == n else x + 1;

'''
    @dev Compute the largest integer smaller than or equal to `x * y / z`
'''
def mulDivF(x, y, z):
    (xyh, xyl) = mul512(x, y);
    if (xyh == 0): # `x * y < 2 ^ 256`
        return xyl // z;
    if (xyh < z): # `x * y / z < 2 ^ 256`
        m = mulMod(x, y, z);            # `m = x * y % z`
        (nh, nl) = sub512(xyh, xyl, m); # `n = x * y - m` hence `n / z = floor(x * y / z)`
        if (nh == 0): # `n < 2 ^ 256`
            return nl // z;
        p = unsafeSub(0, z) & z; # `p` is the largest power of 2 which `z` is divisible by
        q = div512(nh, nl, p);   # `n` is divisible by `p` because `n` is divisible by `z` and `z` is divisible by `p`
        r = inv256(z // p);      # `z / p = 1 mod 2` hence `inverse(z / p) = 1 mod 2 ^ 256`
        return unsafeMul(q, r);  # `q * r = (n / p) * inverse(z / p) = n / z`
    revert(); # `x * y / z >= 2 ^ 256`

'''
    @dev Compute the smallest integer larger than or equal to `x * y / z`
'''
def mulDivC(x, y, z):
    w = mulDivF(x, y, z);
    if (mulMod(x, y, z) > 0):
        return safeAdd(w, 1);
    return w;

'''
    @dev Compute the value of `x * y`
'''
def mul512(x, y):
    p = mulModMax(x, y);
    q = unsafeMul(x, y);
    if (p >= q):
        return (p - q, q);
    return (unsafeSub(p, q) - 1, q);

'''
    @dev Compute the value of `2 ^ 256 * xh + xl - y`, where `2 ^ 256 * xh + xl >= y`
'''
def sub512(xh, xl, y):
    if (xl >= y):
        return (xh, xl - y);
    return (xh - 1, unsafeSub(xl, y));

'''
    @dev Compute the value of `(2 ^ 256 * xh + xl) / pow2n`, where `xl` is divisible by `pow2n`
'''
def div512(xh, xl, pow2n):
    pow2nInv = unsafeAdd(unsafeSub(0, pow2n) // pow2n, 1); # `1 << (256 - n)`
    return unsafeMul(xh, pow2nInv) | (xl // pow2n); # `(xh << (256 - n)) | (xl >> n)`

'''
    @dev Compute the inverse of `d` modulo `2 ^ 256`, where `d` is congruent to `1` modulo `2`
'''
def inv256(d):
    # use newton–raphson convergence method in order to find the root of `f(x) = 1 / x - d`
    x = 1;
    for i in range(8):
        x = unsafeMul(x, unsafeSub(2, unsafeMul(x, d))); # `x = x * (2 - x * d) mod 2 ^ 256`
    return x;
