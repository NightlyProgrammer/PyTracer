
class Material:
    def __init__(self, color, emissionColor = (0,0,0), emissionStrength = 0, roughness = 1, metallic = 0):
        self.color = color
        self.emissionColor = emissionColor
        self.emissionStrength = emissionStrength
        self.roughness = roughness
        self.metallic = metallic
    
    def sendDataToShader(self, program, name):
        program[f"{name}.color"] = self.color
        program[f"{name}.emissionColor"] = self.emissionColor
        program[f"{name}.emissionStrength"] = self.emissionStrength
        program[f"{name}.roughness"] = self.roughness
        program[f"{name}.metallic"] = self.metallic