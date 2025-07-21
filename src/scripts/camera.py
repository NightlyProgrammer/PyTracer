import pygame
from math import sin, cos, radians, pi

from scripts.linear_algebra.matrix import Mat4, Mat3
from scripts.linear_algebra.vector import Vec3

def clamp(x, minval, maxval):
    return min(max(x, minval), maxval)

class Camera:
    def __init__(self, field_of_view=60):
        self.position = Vec3(0, 0, 0)

        self.forward = Vec3(0, 0, 1)
        self.right = Vec3(1, 0, 0)
        self.up = Vec3(0, 1, 0)

        self.moveForward = Vec3(0, 0, 1)
        self.moveRight = Vec3(1, 0, 0)
        self.moveUp = Vec3(0, 1, 0)

        self.yaw, self.pitch = 0, 0

        self.fov = radians(field_of_view)

        self.speed = 10
        self.dirty = False#detect if any changes occured(needs to re start accum)
    
    def getTransformationMatrix(self):
        matrix = Mat4([
            self.right.x, self.right.y, self.right.z, 0,
            self.up.x, self.up.y, self.up.z, 0,
            self.forward.x, self.forward.y, self.forward.z, 0,
            0, 0, 0, 1
        ])

        matrix *= Mat4([
            1, 0, 0, self.position.x,
            0, 1, 0, self.position.y,
            0, 0, 1, self.position.z,
            0, 0, 0, 1
        ])

        return matrix.get_data()
    
    def sendDataToShader(self, program):
        program["u_cameraTransformation"] = self.getTransformationMatrix()
        program["u_fov"] = self.fov
    
    def calcDirectionVectors(self):
        rotationMatrixY = Mat3([
            cos(self.yaw), 0, -sin(self.yaw),
            0, 1, 0,
            sin(self.yaw), 0, cos(self.yaw)
        ])
        rotationMatrixY_inverse = rotationMatrixY.transpose()#transpose of rotation matrix is its inverse
        rotationMatrixX = Mat3([
            1, 0, 0,
            0, cos(self.pitch), sin(self.pitch),
            0, -sin(self.pitch), cos(self.pitch)
        ])

        rotationMatrix = rotationMatrixY * rotationMatrixX

        self.forward = Vec3(0, 0, 1) * rotationMatrix
        self.moveForward = Vec3(0, 0, 1) * rotationMatrixY_inverse
        self.right = Vec3(1, 0, 0) * rotationMatrix
        self.moveRight = Vec3(1, 0, 0) * rotationMatrixY_inverse
        self.up = self.forward.cross_product(self.right)#Vec3(0, 1, 0) * rotationMatrix#self.forward.cross_product(self.right)
        self.moveUp = self.moveForward.cross_product(self.moveRight)
    
    def input(self, delta):
        keys = pygame.key.get_pressed()

        rel = pygame.mouse.get_rel()

        if (rel[0]+rel[1]) < 1000 and (rel[0]+rel[1]) != 0:#cuz on init pygame freaks out
            self.dirty = True
            self.yaw += rel[0] * 0.001
            self.pitch += rel[1] * 0.001

        self.pitch = clamp(self.pitch, -pi/2, pi/2)

        if keys[pygame.K_w]:
            self.dirty = True
            self.position += self.moveForward * delta * self.speed
        if keys[pygame.K_s]:
            self.dirty = True
            self.position -= self.moveForward * delta * self.speed
        if keys[pygame.K_a]:
            self.dirty = True
            self.position -= self.moveRight * delta * self.speed
        if keys[pygame.K_d]:
            self.dirty = True
            self.position += self.moveRight * delta * self.speed
        if keys[pygame.K_SPACE]:
            self.dirty = True
            self.position += self.moveUp * delta * self.speed
        if keys[pygame.K_LSHIFT]:
            self.dirty = True
            self.position -= self.moveUp * delta * self.speed
    
    def update(self, delta):
        self.dirty = False
        self.calcDirectionVectors()
        self.input(delta)