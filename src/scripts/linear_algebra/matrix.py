#all matricies needed to pass data like camera transformation

class Matrix:
    COLUMNS = None
    ROWS = None
    def __init__(self, data):
        self._data = data
    
    def __repr__(self):
        matrix_name = self.__class__.__name__
        return f"{matrix_name}(\n {' '.join([str(d)+'\n'*((i+1)%self.ROWS==0) for i,d in enumerate(self._data)])})"
    
    def create_new_instance(self, data):
        MatrixClass = self.__class__
        return MatrixClass(data)
    
    def set(self, i, j, value):
        self._data[i + j * self.ROWS] = value
    def get(self, i, j):
        return self._data[i + j * self.ROWS]
    
    def get_data(self):
        return self._data
    
    def __mul__(self, other):
        if type(other) == type(self):
            return self.matrix_mul(other)
    
    def matrix_mul(self, other):# Yes is inefficient but most matrix calc happens on the gpu anyways, also dont want to write it our for each differnet kind of matrix
        outcomeMatrix = self.create_new_instance([0 for i in range(self.ROWS * self.COLUMNS)])
        for k in range(self.ROWS):
            for i in range(self.COLUMNS):
                value = sum([self.get(i, j) * other.get(j, k) for j in range(self.COLUMNS)])
                outcomeMatrix.set(i, k, value)
        return outcomeMatrix
    
    def transpose(self):
        data = []
        for j in range(self.ROWS):
            for i in range(self.COLUMNS):
                data.append( self.get(j, i) )
        return self.create_new_instance(data)
    
class Mat3(Matrix):
    COLUMNS = 3
    ROWS = 3

class Mat4(Matrix):
    COLUMNS = 4
    ROWS = 4

if __name__ == '__main__':
    mat = Mat3([
        1,0,2,
        0,1,0,
        0,0,1
    ])
    mat2 = Mat3([
        1,0,0,
        0,1,0,
        2,0,1
    ])
    print(mat)
    print("Transpose", mat.transpose())
    print("Multiplied", mat * mat2)