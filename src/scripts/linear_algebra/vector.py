#vectors
#TODO implement cross product for n-dimensional vector
from scripts.linear_algebra.matrix import Matrix

class Vector:
    def __init__(self, *args):
        self._data = args
    
    def __repr__(self):
        VectorName = self.__class__.__name__
        return f"{VectorName}({' '.join([str(d) for d in self._data])})"
    
    def create_new_instance(self, data):
        VectorClass = self.__class__
        return VectorClass(data)
    
    def __mul__(self, other):
        scalar_types = [int, float]
        if type(other) in scalar_types:
            data = [d * other for d in self._data]
            return self.create_new_instance(data)
        elif type(other) == type(self):
            data = [d * other._data[i] for i,d in enumerate(self._data)]
            return self.create_new_instance(data)
        elif issubclass(other.__class__, Matrix):#check if other is a type of matrix
            #check if number of colums is compatible
            if other.COLUMNS != len(self._data):
                raise ValueError(f"Cant multiply Matrix with {other.COLUMNS} columns with a Vector with {len(self._data)} components!")
            return self.matrix_mul(other)

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def matrix_mul(self, other):
        #for now can only return vector with same number of components, cuz we probably wont need something other than a mxm matrix
        size = len(self._data)
        data = [
            sum([
                self._data[i] * other.get(i, j)
                for i in range(size)
            ])
            for j in range(size)
        ]
        return self.create_new_instance(data)
    
    def __add__(self, other):
        if type(other) == type(self):
            data = [d + other._data[i] for i,d in enumerate(self._data)]
            return self.create_new_instance(data)
    
    def __sub__(self, other):
        if type(other) == type(self):
            data = [d - other._data[i] for i,d in enumerate(self._data)]
            return self.create_new_instance(data)

class Vec3(Vector):
    def __init__(self, x:float | list = 0, y = 0, z = 0):
        if type(x) == list:
            args = x
        else:
            args = x,y,z
        super().__init__(*args)
    
    def __getattr__(self, name):
        match name:
            case "x":
                return self._data[0]
            case "y":
                return self._data[1]
            case "z":
                return self._data[2]
            case "xy":
                return self._data[0], self._data[1]
            case "yz":
                return self._data[1], self._data[2]
            case "xz":
                return self._data[0], self._data[2]
            case "xyz":
                return self._data
            case _:
                raise AttributeError(name)
    
    def cross_product(self, other):
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return self.create_new_instance([x,y,z])

if __name__ == '__main__':
    from matrix import Mat3

    vec = Vec3(10, 5, 1)
    vec2 = Vec3(0, 0, 1)
    vec3 = Vec3(1, 0, 0)
    print("Crossp produvt",vec2.cross_product(vec3))
    
    mat = Mat3([
        1,0,0,
        0,1,0,
        0,0,1
    ])
    print(2 * vec * 10)
    print(vec * mat)
    print(vec.x)
    print(vec.xyz)