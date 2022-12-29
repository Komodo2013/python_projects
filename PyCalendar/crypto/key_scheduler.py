from crypto_utils import SubsBoxes

def rot(_bytes):
    """
    Rotates the bytes left one in an array
    :param _bytes: a list of bytes
    :return: the list of bytes shifted left one
    """
    temp = _bytes[1:]
    temp.append(_bytes[0])
    return temp


def rcon(i):
    """
    Returns the byte to use to xor the first value of the new round key with
    :param i: int the round number
    :return: byte, the result of rcon
    """

    if i == 0:
        return 0
    c = 1

    # I don't understand where these numbers come from. I got them off wikipedia
    while i >= 1:
        b = c & 0x80
        c << 1
        if b == 0x80:
            c ^= 0x1b
        i -= 1

    return c


class KeyScheduler:

    my_subs = SubsBoxes()

    def __init__(self, key_bytes):
        self.key_bytes = []

        if len(key_bytes) != 16:
            raise "Invalid key length"

        for i in range(4):
            self.key_bytes.append([])
            for j in range(4):
                self.key_bytes[i].append(key_bytes[i * 4 + j])
        self.keys = [[]]
        for l in self.key_bytes:
            self.keys[0].append(l[:])

    def generate_keys(self, i):
        for j in range(i):
            if j != 0:
                new_bytes = self.generate_round_key(self.keys[j - 1], j)
                self.keys.append([])
                for l in new_bytes:
                    self.keys[j].append(l[:])
        return self

    def generate_round_key(self, last_bytes, round):
        substituted = self.my_subs.subs(rot(last_bytes[3]))
        temp = []

        for b in substituted:
            temp.append(b)

        temp[0] ^= rcon(round)

        for i in range(4):
            for j in range(4):
                if i == 0:
                    self.key_bytes[i][j] = last_bytes[i][j] ^ temp[j]
                else:
                    self.key_bytes[i][j] = self.key_bytes[i - 1][j] ^ last_bytes[i][j]

        return self.key_bytes

    def get_round_key(self, i):
        return self.keys[i]

    def add_key(self, matrix, i):
        round_key = self.get_round_key(i)
        result = []

        for i in range(len(matrix)):
            result.append([])
            for j in range(len(matrix[i])):
                result[i].append(matrix[i][j] ^ round_key[i][j])

        return result
