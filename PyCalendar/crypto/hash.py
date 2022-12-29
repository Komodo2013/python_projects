from crypto_utils import mix_matrices, string_to_packets, SubsBoxes, mix_columns, shift_rows


def hash_(byte_matrix, iterations):
    """
    Controller for hashing a specific byte_matrix using Rijndael cipher like combinations
    :param byte_matrix: an 8x8 matrix of bytes (ints). Must be 8x8 or out of bounds exception will be raised
    :param iterations: the number of times to repeat the process. I find iterations >= 4 to be sufficiently mixed
    :return: byte_matrix, the resulting 8x8 byte matrix
    """

    s = SubsBoxes()

    for i in range(iterations):
        # operations combined to reduce saving to byte_matrix
        byte_matrix = mix_columns(shift_rows(s.sub_matrix(byte_matrix)))
    return byte_matrix


class MyHash:

    # sample 2d list of bytes (ints). This is the default internal matrix. generated by randInt(0,255) repeated
    # the following table was constructed using digits of pi, taking 2-3 digits so long as its < 256
    # 0's that became leading 0's were omitted, with comments locating each missing 0
    data = (
        [31, 41, 59, 26, 53, 58, 97, 93],
        [238, 46, 26, 43, 38, 32, 79, 50],
        [233, 124, 194, 224, 73, 244, 115, 27],
        [28, 84, 197, 169, 39, 93, 75, 105],
        [82, 97, 49, 44, 59, 230, 78, 164],  # second value 97 would be 097 following pi
        [62, 86, 208, 99, 86, 28, 34, 82],  # first value 62 would be 062 following pi, value 34 would be 034
        [53, 42, 117, 67, 98, 214, 80, 86],  # value 67 would be 067 following pi
        [51, 32, 82, 30, 66, 47, 93, 84]  # value 66 would be 066 following pi again
    )

    def __init__(self, internal_matrix=data):
        """
        constructor function, allows the setting of the internal_matrix upon creation
        :param internal_matrix: List[ List[Int]] 2d list of bytes (ints) to be used as the internal matrix
        """
        self.internal_matrix = []
        for i in range(len(internal_matrix)):
            self.internal_matrix.append(internal_matrix[i][:])

    def hash_packs(self, byte_matrices, iterations):
        """
        Creates a hash matrix from a list of byte matrices using iterations loops per packet
        :param byte_matrices: List [List [ List [Int] ] ] 3d list containing bytes (ints)
        :param iterations: The number of loops for each pack of bytes to run the hash algorithm
        :return: List[ List[Int]] the resulting hashed matrix
        """

        # Initialize the variable for out-of-loop access
        byte_matrix = 0
        # for each byte matrix received
        for i in range(len(byte_matrices)):
            # with first matrix, mix the internal matrix
            if i == 0:
                byte_matrix = mix_matrices(self.internal_matrix, byte_matrices[i])
            # Other iterations, mix our resulting matrix with next
            else:
                byte_matrix = mix_matrices(byte_matrix, byte_matrices[i])

            # new hash function which is more stable, runs faster, and has better distribution
            byte_matrix = hash_(byte_matrix, iterations)

        return byte_matrix

    def set_internal_matrix(self, seed):
        """
        Sets the internal matrix based of the seed provided, using the current internal matrix
        :param seed: String of any size
        :return: self for chaining
        """

        # get packets from the seed
        packets = string_to_packets(seed)

        self.internal_matrix = MyHash().hash_packs(packets, 5)
        return self

    def salt(self):
        self.internal_matrix = hash_(self.internal_matrix, 5)