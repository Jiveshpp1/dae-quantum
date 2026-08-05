import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def bb84_simulation(num_bits=100, eve_present=False):
    print("=" * 65)
    status = "EVE INTERCEPTING" if eve_present else "SECURE CHANNEL (NO EVE)"
    print(f" RUNNING BB84 QKD SIMULATION — {status} ")
    print("=" * 65)

    alice_bits = np.random.randint(0, 2, num_bits)
    alice_bases = np.random.randint(0, 2, num_bits)

    bob_bases = np.random.randint(0, 2, num_bits)

    if eve_present:
        eve_bases = np.random.randint(0, 2, num_bits)

    bob_results = []
    simulator = AerSimulator()

    for i in range(num_bits):
        qc = QuantumCircuit(1, 1)

        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        if eve_present:
            if eve_bases[i] == 1:
                qc.h(0)
            qc.measure(0, 0)
            if eve_bases[i] == 1:
                qc.h(0)

        if bob_bases[i] == 1:
            qc.h(0)
        qc.measure(0, 0)

        compiled_qc = transpile(qc, simulator)
        result = simulator.run(compiled_qc, shots=1).result()
        counts = result.get_counts()
        measured_bit = int(list(counts.keys())[0])
        bob_results.append(measured_bit)

    alice_sifted_key = []
    bob_sifted_key = []

    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            alice_sifted_key.append(alice_bits[i])
            bob_sifted_key.append(bob_results[i])

    sifted_length = len(alice_sifted_key)
    errors = sum(a != b for a, b in zip(alice_sifted_key, bob_sifted_key))
    qber = (errors / sifted_length) * 100 if sifted_length > 0 else 0

    print(f"\n[+] Raw Bits Transmitted:       {num_bits}")
    print(f"[+] Sifted Key Length:          {sifted_length} bits (Bases Matched)")
    print(f"[+] Mismatched Key Bits:        {errors}")
    print(f"[+] Quantum Bit Error Rate:     {qber:.2f}%")

    if qber > 11.0:
        print("\n⚠️  ALERT: High QBER detected! Eavesdropper present on line.")
        print("    STATUS: Key exchange ABORTED. No secure key established.")
    else:
        print("\n✅ SECURE: QBER within acceptable margin.")
        print(f"    STATUS: Shared Secret Key established successfully.")
        print(f"    Sample Key (first 16 bits): {alice_sifted_key[:16]}")
    
    print("=" * 65 + "\n")
    return qber

if __name__ == "__main__":
    qber_clean = bb84_simulation(num_bits=200, eve_present=False)
    qber_intercepted = bb84_simulation(num_bits=200, eve_present=True)

