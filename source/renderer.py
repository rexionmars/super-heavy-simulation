import math
import random
import pygame
import pygame.gfxdraw
from rocket_renderer import RocketRenderer
from constants import WHITE, BLACK, RED, BLUE, ORANGE
from utils import map_value, calculate_top_position, is_rocket_inverted

class Renderer:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.rocket_renderer = RocketRenderer('/home/luisgoc/workspace/super-heavy-simulation/assets/imgs/super_heavy_dark.png', initial_scale=0.5)
        self.trajectory_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 14)
        self.stage_separation_time = 60*2 + 48  # Tempo da separação dos estágios
        self.separation_started = False

    def set_rocket_scale(self, scale):
        self.rocket_renderer.set_scale(scale)

    def render(self, simulation):
        self.screen.fill(WHITE)
        self.draw_full_trajectory(simulation)
        self.screen.blit(self.trajectory_surface, (0, 0))
        self.draw_current_position(simulation)
        self.draw_info(simulation.get_current_data())
        self.draw_axis_labels()

    def draw_full_trajectory(self, simulation):
        self.trajectory_surface.fill((0, 0, 0, 0))  # Clear with transparency
        max_altitude = simulation.get_max_altitude()
        max_downrange = simulation.get_max_downrange()
        
        trajectory_points = []
        for point in simulation.data:
            x = map_value(point['Downrange distance [km]'], 0, max_downrange, self.width * 0.1, self.width * 0.9)
            y = map_value(point['Smoothed altitude [km]'], 0, max_altitude, self.height * 0.9, self.height * 0.1)
            trajectory_points.append((int(x), int(y)))
        
        if len(trajectory_points) > 1:
            pygame.draw.lines(self.trajectory_surface, BLUE, False, trajectory_points, 1)
        
        self.draw_trajectory_events(simulation.data, max_altitude, max_downrange)

    def draw_current_position(self, simulation):
        current_data = simulation.get_current_data()
        current_time = current_data['Time [s]']
        max_altitude = simulation.get_max_altitude()
        max_downrange = simulation.get_max_downrange()
        
        pos_x = map_value(current_data['Downrange distance [km]'], 0, max_downrange, self.width * 0.1, self.width * 0.9)
        pos_y = map_value(current_data['Smoothed altitude [km]'], 0, max_altitude, self.height * 0.9, self.height * 0.1)
        
        angle = self.calculate_angle(current_data)
        
        if current_time >= self.stage_separation_time and not self.separation_started:
            self.separation_started = True
            self.rocket_renderer.start_rotation(angle + 180)
        
        self.rocket_renderer.update_rotation()
        
        rocket_height = self.rocket_renderer.get_height()
        top_x, top_y = calculate_top_position(pos_x, pos_y, self.rocket_renderer.current_angle, rocket_height / 2, current_time)
        
        self.rocket_renderer.render(self.screen, pos_x, pos_y)
        self.draw_fire_particles(pos_x, pos_y, self.rocket_renderer.current_angle, current_data['Smoothed speed [m/s]'], current_time)
        pygame.draw.circle(self.screen, RED, (int(top_x), int(top_y)), 3)

    def draw_info(self, current_data):
        info_text = [
            f"Time: {current_data['Time [s]']:.2f} s",
            f"Altitude: {current_data['Smoothed altitude [km]']:.2f} km",
            f"Speed: {current_data['Smoothed speed [m/s]']:.2f} m/s",
            f"Mach: {current_data['Mach number']:.2f}",
            f"Dynamic Pressure: {current_data['Dynamic pressure [kPa]']:.2f} kPa"
        ]
        for i, text in enumerate(info_text):
            text_surface = self.small_font.render(text, True, BLACK)
            self.screen.blit(text_surface, (10, 10 + i * 20))

    def draw_axis_labels(self):
        title = self.font.render("Trajectory profile", True, BLACK)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 10))
        
        x_label = self.font.render("Downrange distance [km]", True, BLACK)
        self.screen.blit(x_label, (self.width // 2 - x_label.get_width() // 2, self.height - 30))
        
        y_label = self.font.render("Altitude [km]", True, BLACK)
        y_label = pygame.transform.rotate(y_label, 90)
        self.screen.blit(y_label, (10, self.height // 2 - y_label.get_height() // 2))

    def draw_trajectory_events(self, data, max_altitude, max_downrange):
        events = [
            ("Max Q", 60),
            ("MECO", 60*2 + 42),
            ("Stage sep", 60*2 + 48),
            ("Boostback start", 60*2 + 54),
            ("Boostback end", 60*3 + 48),
            ("Gridfins live", 60*6 + 5),
            ("Landing burn", 60*6 + 54),
        ]
        
        for label, time in events:
            point = next(p for p in data if p['Time [s]'] >= time)
            x = map_value(point['Downrange distance [km]'], 0, max_downrange, self.width * 0.1, self.width * 0.9)
            y = map_value(point['Smoothed altitude [km]'], 0, max_altitude, self.height * 0.9, self.height * 0.1)
            
            pygame.draw.circle(self.trajectory_surface, RED, (int(x), int(y)), 3)
            text_surface = self.small_font.render(label, True, BLACK)
            self.trajectory_surface.blit(text_surface, (int(x) + 5, int(y) - 15))

    def draw_fire_particles(self, x, y, angle, speed, time):
        num_particles = int(speed / 10)
        for _ in range(num_particles):
            angle_offset = random.uniform(-30, 30)
            distance = random.uniform(20, 40)
            particle_x = x - distance * math.sin(math.radians(angle + angle_offset))
            particle_y = y + distance * math.cos(math.radians(angle + angle_offset))
            color = random.choice([RED, ORANGE])
            pygame.draw.circle(self.screen, color, (int(particle_x), int(particle_y)), random.randint(1, 3))

    @staticmethod
    def calculate_angle(data):
        return -math.degrees(math.atan2(data['Vertical speed [m/s]'], data['Horizontal speed [m/s]']))