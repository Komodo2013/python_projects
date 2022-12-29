import math

from crypto_utils import galois_multiply, SubsBoxes
from hash import MyHash, hash_
from crypto_utils import shift_rows, inv_shift_rows
from key_scheduler import KeyScheduler

s = SubsBoxes()

def add_round_key(data_matrix, key_matrix):
    """
    Use to both add and invert round key, loops through each element combining with xor
    :param data_matrix: matrix to iterate over to combine
    :param key_matrix: key matrix to iterate over to combine, must be same size as data_matrix
    :return: 2d list of values after combination
    """
    result = []

    rows = len(data_matrix)
    columns = len(data_matrix[0])

    if len(key_matrix) != rows or len(key_matrix[0]) != columns:
        raise "Error combining matrices"

    for r in range(rows):
        result.append([])
        for c in range(columns):
            result[r].append(data_matrix[r][c] ^ key_matrix[r][c])

    return result


multiplicand = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]
multiplicand_inv = [[14, 11, 13, 9], [9, 14, 11, 13], [13, 9, 14, 11], [11, 13, 9, 14]]


def mix_column(column):
    result = [0, 0, 0, 0]
    for i in range(4):
        item = 0
        for j in range(4):
            item ^= galois_multiply(column[j], multiplicand[i][j])
        result[i] = item

    return result


def inv_mix(column):
    result = [0, 0, 0, 0]
    for i in range(4):
        item = 0
        for j in range(4):
            item ^= galois_multiply(column[j], multiplicand_inv[i][j])
        result[i] = item

    return result


def mix_columns(matrix):
    result = []
    for i in range(4):
        result.append(mix_column(matrix[i])[:])
    return result


def inv_mix_columns(matrix):
    result = []
    for i in range(4):
        result.append(inv_mix(matrix[i])[:])
    return result


def encrypt(matrix, batch_key, i):
    k = KeyScheduler(batch_key).generate_keys(i + 1)
    result = []
    for m in matrix:
        result.append(m[:])

    result = k.add_key(result, 0)
    for j in range(i - 2):
        result = k.add_key(mix_columns(shift_rows(s.sub_matrix(result))), j + 1)

    result = k.add_key(shift_rows(s.sub_matrix(result)), i-1)

    return result


def decrypt(matrix, batch_key, i):
    k = KeyScheduler(batch_key).generate_keys(i)
    result = []
    for m in matrix:
        result.append(m[:])

    result = s.inv_sub_matrix(inv_shift_rows(k.add_key(result, i-1)))

    for j in range(i - 2):
        result = s.inv_sub_matrix(inv_shift_rows(inv_mix_columns(k.add_key(result, i - j - 2))))

    return k.add_key(result, 0)

def make_packets(bytes_in):
    num_bytes = len(bytes_in)
    bytes_in = bytearray(bytes_in)

    # Figure out how many packets we'll need for 4x4 matrices of bytes
    num_packs = math.ceil(num_bytes/16)
    for i in range(num_packs * 16 - num_bytes):
        bytes_in.append(0)

    packs = []

    for p in range(num_packs):
        packs.append([])
        for i in range(4):
            v = p * 16 + (i + 1) * 4
            if v <= num_bytes:
                packs[-1].append(bytes_in[v - 4: v])
            elif v - 4 <= num_bytes:
                packs[-1].append([])
                for j in range(4):
                    if v + j - 4 <= num_bytes:
                        packs[-1][-1].append(bytes_in[v + j - 4])
                    else:
                        packs[-1][-1].append(0)
            else:
                packs[-1].append([0, 0, 0, 0])

    return packs


class Encryptor:

    def __init__(self, key):
        key_hash = MyHash().set_internal_matrix(key).internal_matrix
        self.rand = MyHash()
        self.rand.internal_matrix = hash_(key_hash, 5)

    def get_batch_key(self):
        combination = self.rand.internal_matrix[0][:]
        for b in self.rand.internal_matrix[1]:
            combination.append(b)
        _batch = bytearray(combination)
        self.rand.salt()
        return _batch

    def encrypt_file(self, bytes):
        print("--making packets")
        packets = make_packets(bytes)
        results = bytearray()

        print("--encrypting packets")
        for i in range(len(packets)):
            packets[i] = encrypt(packets[i], self.get_batch_key(), 12)

        print("--transforming data")
        for p in packets:
            for r in p:
                for b in r:
                    results.append(b)

        return results

    def decrypt_file(self, bytes):
        print("--making packets")
        packets = make_packets(bytes)
        results = bytearray()

        print("--decrypting packets")
        for i in range(len(packets)):
            packets[i] = decrypt(packets[i], self.get_batch_key(), 12)

        print("--transforming data")
        for p in packets:
            for r in p:
                for b in r:
                    results.append(b)

        for i in range(16):
            if results[-1] == 0x00:
                results = results[:-1]

        return results


api = "2974~Ymjt5hMUEQ5Lay30hzwKSc3o4UPnY6vjhFgz3RSRUAPiMtEWacW6wAIqYV81FX6Y"
e = Encryptor("super secret password")

f = e.encrypt_file(bytes(api, 'utf-8'))

print(f)

d = Encryptor("super secret password")

g = d.decrypt_file(f)

print(g)

