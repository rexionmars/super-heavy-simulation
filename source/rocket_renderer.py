import pygame
import math


class RocketRenderer:
    def __init__(self, image_path, initial_scale=1.0):
        self.original_image = pygame.image.load(image_path)
        self.scale = initial_scale
        self.image = pygame.transform.scale(self.original_image, 
                                            (int(self.original_image.get_width() * self.scale),
                                             int(self.original_image.get_height() * self.scale)))
        self.current_angle = 0
        self.target_angle = 0
        self.rotation_speed = 5  # degrees per frame
        self.is_rotating = False

    def set_scale(self, new_scale):
        self.scale = new_scale
        self.image = pygame.transform.scale(self.original_image, 
                                            (int(self.original_image.get_width() * self.scale),
                                             int(self.original_image.get_height() * self.scale)))

    def get_height(self):
        return self.image.get_height()

    def start_rotation(self, target_angle):
        self.target_angle = target_angle
        self.is_rotating = True

    def update_rotation(self):
        if self.is_rotating:
            if abs(self.current_angle - self.target_angle) < self.rotation_speed:
                self.current_angle = self.target_angle
                self.is_rotating = False
            else:
                direction = 1 if (self.target_angle - self.current_angle + 360) % 360 < 180 else -1
                self.current_angle = (self.current_angle + direction * self.rotation_speed) % 360

    def render(self, surface, pos_x, pos_y):
        rotated_image = pygame.transform.rotate(self.image, self.current_angle)
        new_rect = rotated_image.get_rect(center=(pos_x, pos_y))
        surface.blit(rotated_image, new_rect.topleft)