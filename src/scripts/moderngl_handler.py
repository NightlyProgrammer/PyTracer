import numpy as np

class OpenGlHandler:#handle stuff like loading programs etc
    def __init__(self, app):
        self.app = app

        self.vertex_buffer_objects = []
        self.verex_array_objects = []
        self.programs = []
        self.textures = []
        self.framebuffers = []
    
    def release(self):
        for gl_object in self.vertex_buffer_objects + self.verex_array_objects + self.programs + self.textures + self.framebuffers:
            gl_object.release()

    def create_program(self, shader_name, path='./assets/shaders'):
        vertex_shader_name = shader_name.split('|')[0]
        fragment_shader_name = shader_name.split('|')[-1]

        with open(f"{path}/{vertex_shader_name}.vert","r") as file:
            vertex_data = file.read()
        with open(f"{path}/{fragment_shader_name}.frag","r") as file:
            fragment_data = file.read()
        
        program = self.app.ctx.program(vertex_shader = vertex_data, fragment_shader = fragment_data)
        self.programs.append(program)
        return program
    
    def create_vertex_buffer(self, vertecies):
        data = np.array(vertecies, dtype="f4")
        buffer = self.app.ctx.buffer(data)
        self.vertex_buffer_objects.append(buffer)
        return buffer
    
    def create_vertex_array(self, vertex_buffer, program, *attributes):
        vertex_array = self.app.ctx.vertex_array(program, vertex_buffer, *attributes)
        self.verex_array_objects.append(vertex_array)
        return vertex_array
    
    def create_texture(self,size,components,use=False,data_type="f1") -> int:
        tex = self.app.ctx.texture(size,components,dtype=data_type)
        self.textures.append(tex)
        if use:
            tex.use(len(self.textures)-1)
        return len(self.textures)-1
    def get_texture_by_index(self, index):
        return self.textures[index]

    def create_framebuffer(self, color_attachments = (), depth_attachment = None):
        framebuffer = self.app.ctx.framebuffer(color_attachments=color_attachments, depth_attachment=depth_attachment)
        self.framebuffers.append(framebuffer)
        return framebuffer
