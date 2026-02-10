# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True

import numpy as np
from libc.string cimport memcpy
from libc.math cimport log2

# cnp.import_array()

cpdef (int, int) control(int[:, :] control_bit_list):
	cdef int i, j, bit, inclusion_mask = 0, desired_value_mask = 0
	for i, j in control_bit_list:
		bit = 1 << i
		inclusion_mask |= bit
		if j:
			desired_value_mask |= bit
	return inclusion_mask, desired_value_mask

cpdef double complex[::1] qubit_wise_multiply(int n, double complex[:, ::1] U, int i_w, double complex[::1] a,
                                          int[:, ::1] control_bit_list=None):
	cdef int statevector_size = 1 << n
	cdef int halfblock_size = 1 << i_w
	cdef int block_size = halfblock_size << 1
	cdef int i, bit, b0, offset, i1, i2, inclusion_mask = 0, desired_value_mask = 0
	cdef double complex u00 = U[0, 0], u01 = U[0, 1], u10 = U[1, 0], u11 = U[1, 1]
	cdef double complex[::1] b = np.empty(statevector_size, dtype=np.complex128)
	
	if control_bit_list is not None:
		inclusion_mask, desired_value_mask = control(control_bit_list)
		memcpy(&b[0], &a[0], statevector_size * sizeof(double complex))
	
	for b0 in range(0, statevector_size, block_size):
		for offset in range(halfblock_size):
			i1 = b0 | offset
			if control_bit_list is not None and (i1 & inclusion_mask != desired_value_mask):
				continue
			i2 = i1 | halfblock_size
			b[i1] = u00 * a[i1] + u01 * a[i2]
			b[i2] = u10 * a[i1] + u11 * a[i2]
			
	return b

cpdef double complex[::1] apply_swap(int n, int i_w, int j_w, double complex[::1] a, int[:, ::1] control_bit_list=None):
	cdef int statevector_size = 1 << n
	cdef double complex[::1] b = np.empty(statevector_size, dtype=np.complex128)
	memcpy(&b[0], &a[0], statevector_size * sizeof(double complex))
	
	if i_w == j_w:
		return b
		
	cdef int k, l, inclusion_mask = 0, desired_value_mask = 0
	cdef int antimask_i = ~(1 << i_w)
	cdef int mask_j = 1 << j_w
	cdef double complex temp
	
	if control_bit_list is not None:
		inclusion_mask, desired_value_mask = control(control_bit_list)
	
	for k in range(statevector_size):
		if control_bit_list is not None and (k & inclusion_mask != desired_value_mask):
			continue
		if (k >> i_w) & 1 and not ((k >> j_w) & 1):
			l = (k & antimask_i) | mask_j
			temp = b[k]
			b[k] = b[l]
			b[l] = temp
			
	return b

cpdef inline int rearrange_bits(int n, int[::1] bits):
	cdef int i, return_value = 0
	for i in range(bits.shape[0]):
		return_value |= ((n >> i) & 1) << bits[i]
	return return_value

cpdef double complex[:, ::1] partial_trace(double complex[::1] input_state, int[::1] qubits_to_trace):
	cdef int n = <int>log2(input_state.shape[0])
	cdef int num_traced = qubits_to_trace.shape[0]
	cdef int output_dimension = 1 << (n - num_traced)
	cdef double complex[:, ::1] output_matrix = np.zeros((output_dimension, output_dimension), dtype=np.complex128)
	cdef int[::1] lookup_table = np.empty(output_dimension, dtype=np.int32)
	cdef int i, shared_bits, shared_bits_r, output_row, output_col
	cdef double complex input_row, input_col
	cdef int[::1] qubits_to_keep = np.array([i for i in range(n) if i not in qubits_to_trace], dtype=np.int32)
	
	for i in range(output_dimension):
		lookup_table[i] = rearrange_bits(i, qubits_to_keep)
		
	for shared_bits in range(1 << num_traced):
		shared_bits_r = rearrange_bits(shared_bits, qubits_to_trace)
		for output_row in range(output_dimension):
			input_row = input_state[shared_bits_r | lookup_table[output_row]]
			if input_row.real == 0 and input_row.imag == 0:
				continue
			for output_col in range(output_row + 1):
				input_col = input_state[shared_bits_r | lookup_table[output_col]]
				if input_col.real == 0 and input_col.imag == 0:
					continue
				output_matrix[output_row, output_col] = (output_matrix[output_row, output_col] +
				                                         input_row * input_col.conjugate())
	
	for output_row in range(output_dimension):
		for output_col in range(output_row + 1, output_dimension):
				output_matrix[output_row, output_col] = output_matrix[output_col, output_row].conjugate()
				
	return output_matrix
	
cpdef double stabilizer_renyi_entropy(double complex[::1] state):
	cdef int n = <int>log2(state.shape[0])
	cdef int d = state.shape[0]
	cdef int num_paulis = d * d
	cdef double sum_xi_alpha = 0.0
	cdef double xi_squared
	cdef double complex expectation
	cdef int i
	
	for i in range(num_paulis):
		expectation = pauli_expectation_value(n, i, state)
		xi_squared = expectation.real * expectation.real + expectation.imag * expectation.imag
		sum_xi_alpha += xi_squared * xi_squared
	
	return n - log2(sum_xi_alpha)

cpdef double complex pauli_expectation_value(int n, int pauli_idx, double complex[::1] state):
	cdef int d = 1 << n
	cdef int x_part = pauli_idx & ((1 << n) - 1)
	cdef int z_part = pauli_idx >> n
	cdef double complex result = 0.0
	cdef int i, j
	cdef double complex phase, state_i_conj
	
	for i in range(d):
		j = i ^ x_part
		phase = compute_z_phase(i, z_part, n)
		state_i_conj = state[i].real - 1j * state[i].imag
		result += state_i_conj * phase * state[j]
		
	return result


cdef int compute_z_phase(int basis_state, int z_part, int n):
	cdef int parity = 0
	cdef int i
	
	for i in range(n):
		if (z_part >> i) & 1:
			if (basis_state >> i) & 1:
				parity ^= 1
				
	return -1 if parity else 1
