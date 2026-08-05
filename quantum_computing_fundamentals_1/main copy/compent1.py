import numpy as np
from math import gcd
from fractions import Fraction
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def c_amod15(a, power):
    if a not in [2, 7, 8, 11, 13]:
        raise ValueError("'a' must be 2, 7, 8, 11, or 13")
    
    U = QuantumCircuit(4)
    for _ in range(power):
        if a in [2, 13]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [7, 8]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a in [11]:
            U.swap(0, 2)
            U.swap(1, 3)
        if a in [7, 11, 13]:
            for q in range(4):
                U.x(q)
                
    U_gate = U.to_gate()
    U_gate.name = f"{a}^{power} mod 15"
    return U_gate.control(1)

def qft_dagger(n):
    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

def run_shors_demonstration(N=15, a=7, n_count=4):
    print("=" * 65)
    print(f" DEMONSTRATING SHOR'S ALGORITHM: FACTORING N = {N} (a = {a}) ")
    print("=" * 65)

    qc = QuantumCircuit(n_count + 4, n_count)

    for q in range(n_count):
        qc.h(q)

    qc.x(n_count)

    for q in range(n_count):
        power = 2**q
        qc.append(c_amod15(a, power), [q] + list(range(n_count, n_count + 4)))

    qc.append(qft_dagger(n_count), range(n_count))
    qc.measure(range(n_count), range(n_count))

    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts()

    print("\n[+] Quantum Circuit Execution Complete.")
    print("\n--- MEASURED PHASES & FACTORIZATION ---")

    factors_found = set()
    for output_binary, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        decimal_val = int(output_binary, 2)
        phase = decimal_val / (2**n_count)
        
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator

        print(f"• Measured: |{output_binary}> ({decimal_val:2d}/{2**n_count}) -> Phase: {phase:.4f} -> Estimated Period r = {r}")

        if r % 2 == 0:
            guess1 = gcd(a**(r // 2) - 1, N)
            guess2 = gcd(a**(r // 2) + 1, N)
            
            for g in [guess1, guess2]:
                if g not in [1, N] and N % g == 0:
                    factors_found.add(g)

    print("\n" + "=" * 65)
    if factors_found:
        p = list(factors_found)[0]
        q = N // p
        print(f" SUCCESS: Quantum Circuit factored N = {N} into prime factors: {p} × {q}")
    else:
        print(" Retry: Non-trivial period not measured in this run.")
    print("=" * 65)

if __name__ == "__main__":
    run_shors_demonstration(N=15, a=7)

