
class Scene:#contains all the objects in the scene to render and maybye light if i add "fake" lights later on
    def __init__(self):
        self.objects = []
    
    def add(self, primitive):
        self.objects.append(primitive)
    
    def sendDataToShader(self, program):
        program["spheres_length"] = len(self.objects)
        for i, obj in enumerate(self.objects):
            obj.sendDataToShader(program, f"spheres[{i}]")