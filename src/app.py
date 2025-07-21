import pygame
import moderngl
from sys import exit
from os import listdir
from random import uniform

from scripts.moderngl_handler import OpenGlHandler
from scripts.camera import Camera

from scripts.scene.scene import Scene
from scripts.scene.primitive import Sphere
from scripts.scene.material import Material

class App:
    FPS = 60
    def __init__(self, WINDOW_SIZE=(1280, 720), flags=0):
        pygame.init()
        self.init_gl(WINDOW_SIZE, flags)
        self.screen_size = pygame.display.get_window_size()
        
        self.ctx = moderngl.create_context()
        self.clock = pygame.time.Clock()

        self.gl_handler = OpenGlHandler(self)

        self.raytrace_screen_size = self.screen_size[0] * 2, self.screen_size[1] * 2
        self.raytrace_accumulation_texture = self.gl_handler.create_texture(self.raytrace_screen_size,3,True,"f4")#f4 = float 4 bytes
        tex = self.gl_handler.get_texture_by_index(self.raytrace_accumulation_texture)
        self.raytrace_accumulation_fbo = self.gl_handler.create_framebuffer(color_attachments=(tex))
        self.raytrace_program = self.gl_handler.create_program("raytracer")
        self.raytrace_program["aspect_ratio"] = self.screen_size[1] / self.screen_size[0]
        self.raytrace_program["u_screenSize"] = self.raytrace_screen_size
        self.raytrace_program["u_resultBuffer"] = self.raytrace_accumulation_texture
        buffer = self.gl_handler.create_vertex_buffer([
            -1,  1,
             1,  1,
            -1, -1,
             1, -1
        ])
        self.raytrace_vao = self.gl_handler.create_vertex_array(buffer, self.raytrace_program, "in_position")

        self.maxNumAccumulation = 2048#1024
        self.currentNumAccumulation = 0

        self.post_processing_program = self.gl_handler.create_program("post_processing")
        self.post_processing_program["u_accumulatedTexture"] = self.raytrace_accumulation_texture
        self.post_processing_program["u_screenSize"] = self.raytrace_screen_size
        num = 10
        samplingRange = 0.65
        samplingPositions = [(uniform(-samplingRange, samplingRange), uniform(-samplingRange, samplingRange)) for i in range(num - 1)]
        samplingPositions.append((0,0))
        samplingPositions.extend([(0,0) for i in range(100 - num )])
        self.post_processing_program["u_samplingPositions"] = samplingPositions
        self.post_processing_program["u_numSamplingPositions"] = num
        self.post_processing_vao = self.gl_handler.create_vertex_array(buffer, self.post_processing_program, "in_position")

        self.camera = Camera()

        self.scene = Scene()

        material0 = Material((1,1,1), (0.01, 1, 1), 1)
        sphere0 = Sphere((0,0,-50),40, material0)
        #self.scene.add(sphere0)

        material1 = Material((1,0.1,1), roughness=0.01)
        sphere1 = Sphere((0.5,-0.4,-1),1, material1)
        self.scene.add(sphere1)

        material2 = Material((1,0,0.1))
        sphere2 = Sphere((-0.5,-0.5,1),0.5, material2)
        self.scene.add(sphere2)

        material3 = Material((1, 1, 1),roughness=0.01)
        sphere3 = Sphere((-0.6,-100,1),99, material3)
        self.scene.add(sphere3)

        material4 = Material((1,0,1), (0.8, 0.5, 0.2), 2)
        sphere4 = Sphere((5,2,100),45, material4)
        self.scene.add(sphere4)

        for i in range(10):
            m = Material((uniform(0,1),uniform(0,1),uniform(0,1)),roughness=uniform(0,1))
            s = Sphere((uniform(-20,20),uniform(-20, 20),uniform(-20,20)), uniform(0.2, 5), m)
            self.scene.add(s)
    
    def init_gl(self, WINDOW_SIZE, display_flags):
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_CORE, 1)

        flags = pygame.OPENGL | pygame.DOUBLEBUF
        flags |= display_flags

        if WINDOW_SIZE == (0,0):
            flags |= pygame.FULLSCREEN
        pygame.display.set_mode(WINDOW_SIZE, flags)

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
    
    def destroy(self):
        self.gl_handler.release()
        self.ctx.release()
        pygame.quit()
        exit()
    
    def take_screenshot(self,path="assets/screenshots/"):
        n_of_screenshots = len([img for img in listdir(path) if img.split(".")[-1] == "png"])
        test = pygame.image.frombytes(self.ctx.screen.read(),self.screen_size,"RGB",True)
        pygame.image.save(test,path+f"screenshot{n_of_screenshots}.png")
    
    def mainloop(self):
        delta = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.destroy()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.destroy()
                    elif event.key == pygame.K_0:
                        self.take_screenshot()
            
            self.run(delta)

            pygame.display.flip()
            delta = self.clock.tick(self.FPS) * 0.001
            fps = round(self.clock.get_fps())
            pygame.display.set_caption(f"Fps: {fps}, Accum: {self.currentNumAccumulation}")
    
    def run(self, delta):
        self.update(delta)
        if self.currentNumAccumulation != self.maxNumAccumulation:
            self.render()
        self.currentNumAccumulation += 1
        self.currentNumAccumulation = min(self.currentNumAccumulation, self.maxNumAccumulation)
    
    def update_accumulation(self):
        if self.camera.dirty:
            self.currentNumAccumulation = 0
    
    def update(self, delta):
        self.camera.update(delta)

        self.update_accumulation()

        self.raytrace_program["u_numAccumulatedFrames"] = self.currentNumAccumulation
        self.camera.sendDataToShader(self.raytrace_program)
        self.scene.sendDataToShader(self.raytrace_program)
    
    def render_raytrace(self):
        if self.currentNumAccumulation == 0:
            self.raytrace_accumulation_fbo.clear(0, 0, 0)
        self.raytrace_accumulation_fbo.use()
        self.raytrace_vao.render(mode=moderngl.TRIANGLE_STRIP)
    def render(self):
        self.ctx.clear(1,0,0)
        
        self.render_raytrace()
        self.ctx.screen.use()
        self.post_processing_vao.render(mode=moderngl.TRIANGLE_STRIP)

if __name__ == '__main__':
    app = App()
    app.mainloop()