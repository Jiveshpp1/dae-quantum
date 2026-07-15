from qiskit import QuantumCircuit
import qiskit
qc=qiskit.QuantumCircuit(1)
qc.c(0)
qc.measure_all()
print(qc)