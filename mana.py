import numpy as np
import math

# Pauli matrices
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
I = np.eye(2, dtype=complex)

# "Phase point" operators for 1 qubit
A0 = 0.5 * (I + X + Z + Y)
A1 = 0.5 * (I + X - Z - Y)
A2 = 0.5 * (I - X + Z - Y)
A3 = 0.5 * (I - X - Z + Y)

A_single = [A0, A1, A2, A3]

def tensor_n(*ops):
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out

def wigner_phase_space_operators(n):
    #Return the 4^n phase-point operators A_u for n qubits.
    A_list = []
    for index in range(4**n):
        digits = np.base_repr(index, base=4).zfill(n)
        ops = [A_single[int(d)] for d in digits]
        A_list.append(tensor_n(*ops))
    return A_list

def compute_mana_from_statevector(psi):
    #Compute Mana of a pure state |psi>
    psi = np.array(psi)
    n = int(np.log2(len(psi)))

    # density matrix
    rho = np.outer(psi, psi.conjugate())

    # Wigner operators
    A_ops = wigner_phase_space_operators(n)

    # Wigner function values
    W = np.array([np.real(np.trace(A @ rho)) for A in A_ops])

    # Mana = log (sum |W|)
    mana = math.log(np.sum(np.abs(W)))

    return mana, W
