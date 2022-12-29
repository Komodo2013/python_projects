import math

alpha_numeric_values = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w",
    "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
]

def mix_matrices(matrix1, matrix2):
    """
    Combines two 2d lists of bytes (ints) into one through (a+b) * 31
    31 chosen as first two digits of pi
    :param matrix1: List[ List[Int]] a 2d list holding bytes (ints)
    :param matrix2: List[ List[Int]] a 2d list holding bytes (ints)
    :return: matrix, the resulting 2d list
    """

    # Ensure both matrices are the same size
    if len(matrix1) != len(matrix2) and len(matrix2[0]) != len(matrix1[0]):
        return

    # get sizes of the matrices
    rows = len(matrix1)
    columns = len(matrix1[0])

    # for each row
    for r in range(rows):
        # for each column
        for d in range(columns):
            matrix1[r][d] = (matrix1[r][d] ^ matrix2[r][d])

    return matrix1


def inv_shift_rows(byte_matrix):
    """
    Shifts each row right by n spaces, where n is the index of the row. follows column major order
    This function doesn't necessarily belong here, it isn't used by hash.py but rather encryptor.py
    :param byte_matrix: any sized 2d matrix of values
    :return: The resulting 2d list of values after shifting
    """
    new_matrix = []

    # incidentally, python's .append and .set have the same operation cost....
    for i in range(len(byte_matrix)):
        new_matrix.append([])
        for j in range(len(byte_matrix[0])):
            # (j*3 + i) % len(byte_matrix[0]) is what I use to shift the column each index
            new_matrix[i].append(byte_matrix[(j * 3 + i) % len(byte_matrix[0])][j])

    return new_matrix


def shift_rows(byte_matrix):
    """
    Shifts each row left by n spaces, where n is the index of the row. rows are defined as the nth index of each list
    :param byte_matrix: any sized 2d matrix of values
    :return: The resulting 2d list of values after shifting
    """
    new_matrix = []

    # incidentally, python's .append and .set have the same operation cost....
    for i in range(len(byte_matrix)):
        new_matrix.append([])
        for j in range(len(byte_matrix[0])):
            # (j + i) % len(byte_matrix[0]) is what I use to shift the column each index
            new_matrix[i].append(byte_matrix[(j + i) % len(byte_matrix[0])][j])

    return new_matrix


def mix_columns(byte_matrix):
    """
    Mixes each value of one sub list in an 8x8 matrix of ints. This operation is practically irreversible and is
    responsible for the security of the hash. It depends on solving x = [8 ints] where x * vector = output.
    :param byte_matrix: a 8x8 matrix of bytes (ints) to operate on
    :return: the resulting 8x8 matrix from the operation
    """

    """
    Deeper dive into the security here:
    let x = [8 ints] or one of the sub lists of the 2d list
    and v = [2, 3, 5, 7, 11, 13, 17, 19] being first 8 prime numbers 
    one must solve z = y % 256 where y = x[0] * v[0] ^ x[1] * v[1] ... ^ x[7] * v[7]
    to be able to undo this function. Given the difficulty of solving ^ without at least 2 bytes, and the use of % 256
    there should not be a more efficient method to determine z other than brute force.
    Word of caution: since one cannot prove the null, I cannot tell you there isn't a way to solve it, just I can't

    The only weakness I see is that a ^ ... ^ z would = 0 if each value a-z had a matching pair. the odds of this 
    happening are incredibly low... < 1e-14, as that is the chance of a single match occurring. If it did happen, then
    you still don't know which values match ie a with b? d? e? and thus cannot reverse the function 
    """
    new_matrix = [[], [], [], [], [], [], [], []]
    vector = [2, 3, 5, 7, 11, 13, 17, 19]

    for i in range(len(byte_matrix)):
        for j in range(len(byte_matrix[0])):
            val = 0
            for k in range(len(vector)):
                val = val ^ (byte_matrix[i][(j + k) % len(byte_matrix[0])] * vector[k])

            new_matrix[i].append(val % 256)

    return new_matrix


def create_packets(bytes_in):
    """
    Takes in a blob of bytes and divides them into a 3d list of 2d 8x8 matrices of bytes, fills by column
    :param bytes_in: a byte_array of any size
    :return: a 3d list of 2d 8x8 matrices of bytes where each matrix is defined as a packet
    """

    # Figure out how many packets we'll need
    num_packs = math.ceil(len(bytes_in) / 64)

    # iterator for the byte_array
    num_parsed = 0
    pack = [0, 0, 0, 0, 0, 0, 0, 0]
    data_packs = []
    for p in range(num_packs):
        data_packs.append(0)
        tailing_lines = 0
        remainder = []
        for row in range(8):
            to_append = []
            if num_parsed + 8 <= len(bytes_in):
                part = bytes_in[num_parsed:num_parsed + 8]
                for n in part:
                    to_append.append(n)
            else:
                if tailing_lines == 0:
                    tailing_lines += 1
                    part = bytes_in[num_parsed:]
                    for n in part:
                        remainder.append(n)
                    remainder.append(128)
                    while len(remainder) < (8 - row) * 8 - 1:
                        remainder.append(0)
                    remainder.append(7)

                    to_append = remainder[0:8]
                else:
                    to_append = remainder[tailing_lines * 8: tailing_lines * 8 + 8]
                    tailing_lines += 1
            pack[row] = to_append[:]
            num_parsed += 8
        data_packs[p] = pack[:]

    return data_packs


def packets_from_file(location):
    """
    Opens a file at location: location as a byte_array
    :param location: String the location of the file to open
    :return: 3d list of 8x8 byte matrices
    """

    # read each line of the file and copy all into one massive string
    raw = ""
    with open(location) as file:
        for line in file:
            raw += line

        # then change massive string into a bytearray
        raw_bytes = bytearray(raw, 'utf-8')

        # change bytearray into packets
    return create_packets(raw_bytes)


def packet_to_alpha_numeric(matrix):
    """
    Transforms a singe packet into an alpha_numeric representation of the value
    TODO: we can change this to actually read in bits, 6 at a time to get more characters, as is just takes lsbits
    :param matrix: a 2d list containing ints (bytes)
    :return: String a representation of the values, 2 bits lost/ byte
    """
    text = ""
    for r in matrix:
        for c in r:
            char = alpha_numeric_values[c % len(alpha_numeric_values)]
            text += char
    return text


def string_to_packets(string):
    """
    Creates a list of 8x8 matrices of bytes representing the input
    :param string: A string of any size to be converted
    :return:
    """
    return create_packets(bytearray(string, 'utf-8'))


def galois_multiply(a, b):
    p = 0x00
    for i in range(8):
        if b & 0x01 == 0x01:
            p ^= a
        b = b >> 1
        if a & 0x80 == 0x80:
            a = (a << 1) % 256
            a ^= 0x1b
        else:
            a = (a << 1) % 256
    return p


def c_shift(b, n):
    """
    Cyclically shifts a byte left n bits
    :param b: the byte to shift
    :param n: the number of bits to shift
    :return: byte after shifting
    """
    return ((b << n) % 256) | (b >> (8 - n))


def s_box_function(b):
    """
    Substitution calculation, able to run fairly quickly. Unfortunately, the function does not return the values
    stated by the wiki page on "Rijndael S-box". bytes are mapped, so one byte always returns one other byte
    :param b: the byte to substitute
    :return: byte after substitution
    """
    return b ^ c_shift(b, 1) ^ c_shift(b, 2) ^ c_shift(b, 3) ^ c_shift(b, 4) ^ 99


def inv_s_box_function(b):
    """
    Inverse substitution calculation, able to run fairly quickly. Unfortunately, the function does not return the values
    stated by the wiki page on "Rijndael S-box". Incidentally, it does undo the s_box_function(), so still works =D
    :param b: the byte to substitute
    :return: byte after substitution
    """
    return c_shift(b, 1) ^ c_shift(b, 3) ^ c_shift(b, 6) ^ 0x05


class SubsBoxes:
    """
    Contains the functions necessary for dealing with byte substitutions
    """

    s_box = []
    i_box = []

    def __init__(self):
        """
        Populates the two substitution lists
        """
        for i in range(256):
            self.s_box.append(s_box_function(i))
            self.i_box.append(inv_s_box_function(i))

    def sub(self, b):
        """
        Substitutes byte b through bitwise operations
        :param b: byte value to calculate byte substitution
        :return:
        """
        return self.s_box[b]

    def inv(self, b):
        """
        Inverts substituted byte b through bitwise operations
        :param b: byte value to be invert substitution through calculation
        :return:
        """
        return self.i_box[b]

    def subs(self, _bytes):
        """
        foreach byte loop using look-up table for byte substitution
        :param _bytes: bytearray to be iterated and substituted through look-ups
        :return: bytearray the result after substituting each byte
        """
        result = bytearray()
        for b in _bytes:
            result.append(self.sub(b))
        return result

    def sub_matrix(self, _matrix):
        result = []
        for r in _matrix:
            result.append([])
            m = self.subs(r)
            for b in m:
                result[-1].append(b)

        return result

    def inv_sub_matrix(self, _matrix):
        result = []
        for r in _matrix:
            result.append([])
            m = self.invs(r)
            for b in m:
                result[-1].append(b)

        return result

    def invs(self, _bytes):
        """
        foreach byte loop using look-up table for inverting byte substitution
        :param _bytes: bytearray to be iterated and invert substituted through look-ups
        :return: bytearray the result after invert substituting each byte
        """
        result = bytearray()
        for b in _bytes:
            result.append(self.inv(b))
        return result
