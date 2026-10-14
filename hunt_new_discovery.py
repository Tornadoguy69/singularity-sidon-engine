#!/usr/bin/env python3
"""
hunt_new_discovery.py
=====================
Pushes past the N=100 / N=136 / N=183 finite frontier for Erdős Problem #156
(OEIS A382397 & A399118) using Bit-Parallel Contiguous-Span Maximization
and Exact Last-2-Elements Bitmask Completion.

Goal:
  For k = 8, 9, 10, find explicit 0-based Sidon rulers R = {0 = r_1 < r_2 < ... < r_k = L}
  whose blocked set B(R) = R U ((R+R)/2) U (R+R-R) contains a maximal contiguous interval
  [s_min, s_max] enclosing [0, L].
  By Translation Invariance, any such ruler R immediately certifies m(N) <= k for ALL
  N <= (s_max - s_min + 1), with explicit 1-based certificate A = R + (1 - s_min)!
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

import random
import time
from typing import List, Set, Tuple, Optional


def verify_maximal_sidon_independent(A: Set[int], N: int) -> Tuple[bool, str]:
    """Independent definition-level verifier for Sidon property and maximality in {1..N}."""
    A_set = set(A)
    if len(A_set) != len(A):
        return False, "FAIL: Duplicate elements"
    for a in A_set:
        if not isinstance(a, int) or a < 1 or a > N:
            return False, f"FAIL: Element {a} out of range 1..{N}"

    sorted_A = sorted(A_set)
    seen_sums = {}
    for i, a in enumerate(sorted_A):
        for b in sorted_A[i:]:
            s = a + b
            if s in seen_sums:
                pa, pb = seen_sums[s]
                return False, f"FAIL (Not Sidon): {a}+{b} == {pa}+{pb} == {s}"
            seen_sums[s] = (a, b)

    for x in range(1, N + 1):
        if x in A_set:
            continue
        if (2 * x) in seen_sums:
            continue
        if any((x + a) in seen_sums for a in sorted_A):
            continue
        return False, f"FAIL (Not Maximal): x={x} can still be added to A={sorted_A}"

    return True, f"VERIFIED [N={N:3d}, k={len(A_set):2d}, k/N^(1/3)={len(A_set)/(N**(1/3)):.4f}] A={sorted_A}"


def ruler_contiguous_span(ruler: List[int], offset: int = 512) -> Tuple[int, int, int]:
    """
    Given a valid 0-based Sidon ruler `ruler` = [0, r_2, ..., r_k],
    computes its exact blocked bitmask B(R) shifted by +offset and finds the
    longest contiguous run of 1-bits [s_min, s_max] that encloses [0, r_k].
    Returns (span_length, s_min, s_max).
    """
    L = ruler[-1]
    A_mask = 0
    sums_mask = 0
    for r in ruler:
        A_mask |= (1 << r)
    for i, a in enumerate(ruler):
        for b in ruler[i:]:
            sums_mask |= (1 << (a + b))

    # Build blocked_mask shifted by +offset so negative integers are positive bit positions
    blk = 0
    sums_shifted = sums_mask << offset
    for c in ruler:
        blk |= (1 << (c + offset))
        blk |= (sums_shifted >> c)
        for a in ruler:
            s = a + c
            if (s & 1) == 0:
                blk |= (1 << ((s >> 1) + offset))

    # First check if [0, L] itself is 100% covered!
    interior_mask = ((1 << (L + 1)) - 1) << offset
    if (blk & interior_mask) != interior_mask:
        # Count how many interior elements in [0, L] are covered as a partial score
        covered_in_L = (blk & interior_mask).bit_count()
        return covered_in_L - (L + 1), 0, 0  # Negative score = number of holes in [0, L]

    # Expand left from 0 and right from L while bits are 1
    s_min = 0
    while (blk & (1 << (s_min - 1 + offset))) != 0:
        s_min -= 1
    s_max = L
    while (blk & (1 << (s_max + 1 + offset))) != 0:
        s_max += 1

    return (s_max - s_min + 1), s_min, s_max


def is_sidon_ruler(ruler: List[int]) -> bool:
    sums = set()
    for i, a in enumerate(ruler):
        for b in ruler[i:]:
            s = a + b
            if s in sums:
                return False
            sums.add(s)
    return True


def hunt_max_span_ruler(
    k: int, L_min: int, L_max: int, time_budget_sec: float = 12.0, seed: int = 42
) -> Tuple[int, List[int], int]:
    """
    Evolutionary + Tabu + Exact-Leaf-Completion hunter for k-element Sidon rulers
    maximizing contiguous blocked span N_max.
    Given any (k-1)-element prefix [0, r_2, ..., r_{k-1}], evaluates candidate final
    marks r_k in [L_min, L_max] using fast bitmasks to find the exact best completion!
    """
    rng = random.Random(seed)
    offset = 512
    best_span = -999
    best_cert_1based: List[int] = []
    best_ruler: List[int] = []

    t_start = time.time()
    trials = 0

    # Seed with known optimal rulers if applicable
    known_seeds = {
        8: [0, 39, 47, 51, 52, 61, 67, 101], # Verified span 136
        7: [0, 24, 27, 35, 39, 41, 75],      # Verified span 101
    }
    elite_prefixes: List[Tuple[int, List[int]]] = []
    if k in known_seeds:
        seed_r = known_seeds[k]
        span_s, s_min, s_max = ruler_contiguous_span(seed_r, offset=offset)
        if span_s > 0:
            cert_init = [r + (1 - s_min) for r in seed_r]
            ok, msg = verify_maximal_sidon_independent(set(cert_init), span_s)
            if ok:
                best_span = span_s
                best_ruler = seed_r
                best_cert_1based = cert_init
                print(f"  [k={k:2d} | 0.00s | SEED KNOWN] BASELINE SPAN N = {best_span:3d} | {msg}")
                elite_prefixes.append((span_s, seed_r[:-1]))

    while time.time() - t_start < time_budget_sec:
        trials += 1
        # Either mutate an elite prefix or generate a fresh randomized prefix of size k - 1
        if elite_prefixes and rng.random() < 0.75:
            _, base_pref = rng.choice(elite_prefixes)
            pref = list(base_pref)
            # Mutate 1 or 2 interior elements of the prefix
            num_mut = 1 if rng.random() < 0.7 else 2
            for _ in range(num_mut):
                idx = rng.randint(1, k - 2)
                cand_val = pref[idx] + rng.choice([-4, -3, -2, -1, 1, 2, 3, 4, -6, 6])
                if 1 <= cand_val < L_max and cand_val not in pref:
                    new_pref = sorted(pref[:idx] + [cand_val] + pref[idx + 1 :])
                    if is_sidon_ruler(new_pref):
                        pref = new_pref
        else:
            # Generate fresh Sidon prefix of size k - 1 in [0, L_max - 1]
            target_L = rng.randint(L_min, L_max)
            pref = [0]
            sums = {0}
            pool = list(range(1, target_L))
            rng.shuffle(pool)
            for x in pool:
                if (2 * x) not in sums and all((x + a) not in sums for a in pref):
                    for a in pref:
                        sums.add(x + a)
                    sums.add(2 * x)
                    pref.append(x)
                    if len(pref) == k - 1:
                        break
            pref.sort()
            if len(pref) < k - 1:
                continue

        # Precompute bitmasks for the (k - 1)-element prefix `pref`
        A_mask = 0
        sums_mask = 0
        for a in pref:
            A_mask |= (1 << a)
        for i, a in enumerate(pref):
            for b in pref[i:]:
                sums_mask |= (1 << (a + b))

        base_blk = 0
        sums_shifted = sums_mask << offset
        for c in pref:
            base_blk |= (1 << (c + offset))
            base_blk |= (sums_shifted >> c)
            for a in pref:
                s = a + c
                if (s & 1) == 0:
                    base_blk |= (1 << ((s >> 1) + offset))

        # Sweep candidate final elements r_k in [max(L_min, pref[-1]+1), L_max]
        local_best_span = -999
        local_best_rk = -1

        start_rk = max(L_min, pref[-1] + 1)
        for rk in range(start_rk, L_max + 1):
            new_sums = (A_mask << rk) | (1 << (2 * rk))
            if (sums_mask & new_sums) != 0:
                continue
            next_sums = sums_mask | new_sums
            blk = base_blk | (1 << (rk + offset)) | ((next_sums << offset) >> rk)
            new_sums_shifted = new_sums << offset
            for a in pref:
                blk |= (new_sums_shifted >> a)
                s = rk + a
                if (s & 1) == 0:
                    blk |= (1 << ((s >> 1) + offset))

            interior_mask = ((1 << (rk + 1)) - 1) << offset
            if (blk & interior_mask) != interior_mask:
                score = (blk & interior_mask).bit_count() - (rk + 1)
            else:
                s_min = 0
                while (blk & (1 << (s_min - 1 + offset))) != 0:
                    s_min -= 1
                s_max = rk
                while (blk & (1 << (s_max + 1 + offset))) != 0:
                    s_max += 1
                score = s_max - s_min + 1

            if score > local_best_span:
                local_best_span = score
                local_best_rk = rk

            if score > best_span and score > 0:
                full_ruler = pref + [rk]
                span, s_min, s_max = ruler_contiguous_span(full_ruler, offset=offset)
                if span > best_span:
                    cert_1based = [r + (1 - s_min) for r in full_ruler]
                    ok, msg = verify_maximal_sidon_independent(set(cert_1based), span)
                    if ok:
                        best_span = span
                        best_ruler = full_ruler
                        best_cert_1based = cert_1based
                        elapsed = time.time() - t_start
                        print(f"  [k={k:2d} | {elapsed:5.2f}s | trial {trials:5d}] NEW MAX SPAN N = {best_span:3d} | {msg}")

        if local_best_rk != -1:
            elite_prefixes.append((local_best_span, pref))
            elite_prefixes.sort(key=lambda item: item[0], reverse=True)
            if len(elite_prefixes) > 40:
                elite_prefixes = elite_prefixes[:25]

    return best_span, best_ruler, len(best_cert_1based)


if __name__ == "__main__":
    print("=" * 88)
    print("ERDŐS #156 FRONTIER HUNTER: PUSHING BEYOND N=100, N=136, AND N=183 (k = 8, 9, 10)")
    print("=" * 88)

    # 1. Hunt k = 8 (Published A382397 table stops at N=136; theoretical max for k=8 is 152)
    print("\n--- Hunting k = 8 Maximal Sidon Rulers (Target: N > 136) ---")
    span8, ruler8, _ = hunt_max_span_ruler(k=8, L_min=85, L_max=125, time_budget_sec=8.0, seed=108)

    # 2. Hunt k = 9 (Target: N in 153..183)
    print("\n--- Hunting k = 9 Maximal Sidon Rulers (Target: N > 152) ---")
    span9, ruler9, _ = hunt_max_span_ruler(k=9, L_min=110, L_max=160, time_budget_sec=10.0, seed=109)

    # 3. Hunt k = 10 (Uncharted Frontier: N > 183!)
    print("\n--- Hunting k = 10 Maximal Sidon Rulers (Uncharted Frontier Target: N > 183) ---")
    span10, ruler10, _ = hunt_max_span_ruler(k=10, L_min=135, L_max=210, time_budget_sec=15.0, seed=110)

    print("\n" + "=" * 88)
    print("SUMMARY OF DISCOVERED CONTIGUOUS MAXIMAL SIDON SPANS:")
    print(f"  k =  8 : Max Verified N = {span8}  (Ruler: {ruler8})")
    print(f"  k =  9 : Max Verified N = {span9}  (Ruler: {ruler9})")
    print(f"  k = 10 : Max Verified N = {span10} (Ruler: {ruler10})")
    print("=" * 88)
