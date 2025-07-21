
class Primitive:
    def __init__(self, material):
        self.material = material

    def sendDataToShader(self, program, name):
        pass

class Sphere(Primitive):
    def __init__(self, position, radius, material):
        super().__init__(material)
        self.position = position
        self.radius = radius
        self.material = material
    
    def sendDataToShader(self, program, name):
        program[f"{name}.position"] = self.position
        program[f"{name}.radius"] = self.radius
        self.material.sendDataToShader(program, f"{name}.material")