# Designed for use of the Curve25519 as defined:
# y**2 ≡ x**3 + 486662x**2 + x (mod 2**255 - 19)
from collections import namedtuple
Point = namedtuple("Point", "x y")


class Curve:

    Origin = 'Origin'

    def __init__(self):
        self.A = 486662
        self.B = 1
        self.K = 2 ** 255 - 19
        self.Order = 2 ** 252 + 27742317777372353535851937790883648493
        self.G = Point(9, 14781619447589544791020593568409986887264606134616475288964881837755586237401)

    def define_curve(self, a, b, k, order, g):
        self.A = a
        self.B = b
        self.K = k
        self.Order = order
        self.G = g

    def is_valid_point(self, p):
        """
        Determine whether we have a valid representation of a point
        on our curve.  We assume that the x and y coordinates
        are always reduced modulo p, so that we can compare
        two points for equality with a simple ==.
        """
        if p == self.Origin:
            return True
        else:
            return (
                    (self.B * p.y ** 2 - (p.x ** 3 + self.A * p.x ** 2 + p.x)) % self.K == 0 and
                    0 <= p.x < self.K and 0 <= p.y < self.K)

    def inv_mod_p(self, x):
        """
        Compute an inverse for x modulo p, assuming that x
        is not divisible by p.
        """
        if x % self.K == 0:
            raise ZeroDivisionError("Impossible inverse")
        return pow(x, self.K-2, self.K)

    def ec_inv(self, p):
        """
        Inverse of the point P on the elliptic curve
        """
        if p == self.Origin:
            return p
        return Point(p.x, (-p.y) % self.K)

    def point_double(self, p):
        l = ((3 * p.x ** 2 + 2 * self.A * p.x + 1) * self.inv_mod_p(2 * self.B * p.y))
        x = (self.B * l ** 2 - self.A - 2 * p.x) % self.K
        y = ((3 * p.x + self.A) * l - self.B * l ** 3 - p.y) % self.K
        return Point(x, y)

    def point_addition(self, p1, p2):
        x3 = ((self.B * (p2.y - p1.y) ** 2) * self.inv_mod_p((p2.x - p1.x) ** 2) - self.A - p1.x - p2.x) % self.K
        y3 = ((2 * p1.x + p2.x + self.A) * (p2.y - p1.y) * self.inv_mod_p((p2.x - p1.x)) - self.B * (p2.y - p1.y) ** 3 *
              self.inv_mod_p((p2.x - p1.x) ** 3) - p1.y) % self.K
        return Point(x3, y3)

    def point_calc(self, p1, p2):
        if not (self.is_valid_point(p1) and self.is_valid_point(p2)):
            raise ValueError('Input is not a valid point')

        if p1 == self.Origin:
            return p2
        elif p2 == self.Origin:
            return p1
        elif p1 == self.ec_inv(p2):
            return self.Origin
        else:
            if p1 == p2:
                return self.point_double(p1)
            else:
                return self.point_addition(p1, p2)

    def multiply_np(self, n, p):
        pmultplier = p
        p2 = p
        n = n - 1
        while n > 0:
            if n & 1:
                p2 = self.point_calc(p2, pmultplier)

            pmultplier = self.point_double(pmultplier)
            n = n >> 1
        return p2
