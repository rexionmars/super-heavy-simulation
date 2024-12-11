import pygame
import math
import random
import csv
import pygame.gfxdraw
from svgpathtools import svg2paths, Path

# Inicializar Pygame
pygame.init()

# Configurações da janela
width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Super Heavy Atmospheric Reentry - Real Data Simulation")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255, 128)

# Configuração da espessura da linha
TRAJECTORY_LINE_THICKNESS = 1

def draw_trajectory_points(surface, data, max_altitude, max_downrange):
    font = pygame.font.Font(None, 14)
    for point in data[::60]:  # A cada 60 pontos (assumindo 1 ponto por segundo)
        x = map_value(point['Downrange distance [km]'], 0, max_downrange, width * 0.1, width * 0.9)
        y = map_value(point['Smoothed altitude [km]'], 0, max_altitude, height * 0.9, height * 0.1)
        pygame.draw.circle(surface, BLACK, (int(x), int(y)), 3)
        
        # Adicionar rótulo de tempo
        time_text = f"{point['Time [s]']:.0f} s"
        text_surface = font.render(time_text, True, BLACK)
        surface.blit(text_surface, (int(x) + 5, int(y) - 15))

def draw_trajectory_events(surface, data, max_altitude, max_downrange):
    events = [
        ("Max Q", 60),
        ("MECO", 60*2 + 42),
        ("Stage sep", 60*2 + 48),
        ("Boostback start", 60*2 + 54),
        ("Boostback end", 60*3 + 48),
        ("Gridfins live", 60*6 + 5),
        ("Landing burn", 60*6 + 54),
    ]
    
    font = pygame.font.Font(None, 18)
    for label, time in events:
        point = next(p for p in data if p['Time [s]'] >= time)
        x = map_value(point['Downrange distance [km]'], 0, max_downrange, width * 0.1, width * 0.9)
        y = map_value(point['Smoothed altitude [km]'], 0, max_altitude, height * 0.9, height * 0.1)
        
        pygame.draw.circle(surface, RED, (int(x), int(y)), 4)
        text_surface = font.render(label, True, BLACK)
        surface.blit(text_surface, (int(x) + 5, int(y) - 15))

# Função para analisar a orientação do SVG
def analyze_svg_orientation(paths):
    ymin = float('inf')
    ymax = float('-inf')
    xmin = float('inf')
    xmax = float('-inf')
    
    for path in paths:
        for segment in path:
            for point in [segment.start, segment.end]:
                ymin = min(ymin, point.imag)
                ymax = max(ymax, point.imag)
                xmin = min(xmin, point.real)
                xmax = max(xmax, point.real)
    
    top_width = 0
    bottom_width = 0
    threshold = (ymax - ymin) * 0.5
    
    for path in paths:
        for segment in path:
            for point in [segment.start, segment.end]:
                if abs(point.imag - ymin) < threshold:
                    top_width = max(top_width, abs(point.real - xmin))
                elif abs(point.imag - ymax) < threshold:
                    bottom_width = max(bottom_width, abs(point.real - xmin))
    
    return "normal" if top_width < bottom_width else "inverted"

# Carregar o SVG e determinar sua orientação
paths, attributes = svg2paths('/home/luisgoc/workspace/super-heavy-simulation/assets/imgs/super_heavy.svg')
svg_orientation = analyze_svg_orientation(paths)
print(f"Orientação do SVG: {svg_orientation}")

# Calcular o centro e as dimensões do SVG
def get_svg_bounds(paths):
    xmin, xmax, ymin, ymax = float('inf'), float('-inf'), float('inf'), float('-inf')
    for path in paths:
        for segment in path:
            for point in [segment.start, segment.end]:
                xmin = min(xmin, point.real)
                xmax = max(xmax, point.real)
                ymin = min(ymin, point.imag)
                ymax = max(ymax, point.imag)
    return xmin, xmax, ymin, ymax

xmin, xmax, ymin, ymax = get_svg_bounds(paths)
svg_width = xmax - xmin
svg_height = ymax - ymin
svg_center_x = (xmin + xmax) / 2
svg_top_y = ymin if svg_orientation == "normal" else ymax

# Calcular fator de escala
scale = min(width * 0.1 / svg_width, height * 0.2 / svg_height)

# Criar uma superfície para desenhar com anti-aliasing
drawing_surface = pygame.Surface((width, height), pygame.SRCALPHA)

# Carregar dados do CSV
data = []
with open('/home/luisgoc/workspace/super-heavy-simulation/assets/data/IFT3_full_data_booster.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        data.append({k: float(v) if v else 0 for k, v in row.items()})

# Função para determinar se o foguete está invertido
def is_rocket_inverted(time):
    boostback_end_time = 60*3 + 48  # Tempo do Boostback end
    return time > boostback_end_time

def calculate_top_position(pos_x, pos_y, angle, rocket_height, time):
    if is_rocket_inverted(time):
        angle += 180  # Inverte o ângulo se o foguete estiver de cabeça para baixo
    
    if svg_orientation == "normal":
        top_x = pos_x + rocket_height * math.sin(math.radians(angle))
        top_y = pos_y - rocket_height * math.cos(math.radians(angle))
    else:
        top_x = pos_x - rocket_height * math.sin(math.radians(angle))
        top_y = pos_y + rocket_height * math.cos(math.radians(angle))
    return top_x, top_y

# Funções de utilidade
def map_value(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

def rotate_point(x, y, cx, cy, angle):
    rad = math.radians(angle)
    dx = x - cx
    dy = y - cy
    rotated_x = cx + dx * math.cos(rad) - dy * math.sin(rad)
    rotated_y = cy + dx * math.sin(rad) + dy * math.cos(rad)
    return rotated_x, rotated_y

def draw_aa_line(surface, color, start_pos, end_pos, width=1):
    pygame.draw.line(surface, color, start_pos, end_pos, width)

# Função para desenhar o SVG
def draw_svg(surface, paths, angle, pos_x, pos_y, time):
    surface.fill((0, 0, 0, 0))  # Limpar com transparência
    
    if is_rocket_inverted(time):
        angle += -90  # Inverte o ângulo se o foguete estiver de cabeça para baixo
    
    rotation_point_y = (ymin - svg_top_y) * scale if svg_orientation == "normal" else (ymax - svg_top_y) * scale
    
    for path in paths:
        points = []
        for segment in path:
            start = segment.start
            end = segment.end
            scaled_start_x = (start.real - svg_center_x) * scale
            scaled_start_y = (start.imag - svg_top_y) * scale
            scaled_end_x = (end.real - svg_center_x) * scale
            scaled_end_y = (end.imag - svg_top_y) * scale
            
            if svg_orientation == "inverted":
                scaled_start_y = -scaled_start_y
                scaled_end_y = -scaled_end_y
            
            rotated_start = rotate_point(scaled_start_x, scaled_start_y, 0, rotation_point_y, angle)
            rotated_end = rotate_point(scaled_end_x, scaled_end_y, 0, rotation_point_y, angle)
            
            points.extend([(rotated_start[0] + pos_x, rotated_start[1] + pos_y - rotation_point_y),
                           (rotated_end[0] + pos_x, rotated_end[1] + pos_y - rotation_point_y)])
        
        if len(points) >= 2:
            for i in range(0, len(points) - 1, 2):
                draw_aa_line(surface, BLACK, points[i], points[i+1], 1)

# Função para desenhar partículas de fogo
def draw_fire_particles(surface, x, y, angle, speed, time):
    num_particles = int(speed / 10)
    particle_angle = angle
    if is_rocket_inverted(time):
        particle_angle += 180
    for _ in range(num_particles):
        angle_offset = random.uniform(-30, 30)
        distance = random.uniform(20, 40)
        particle_x = x + distance * math.sin(math.radians(particle_angle + angle_offset))
        particle_y = y + distance * math.cos(math.radians(particle_angle + angle_offset))
        color = random.choice([RED, ORANGE])
        pygame.draw.circle(surface, color, (int(particle_x), int(particle_y)), random.randint(1, 3))

# Função para desenhar informações na tela
def draw_info(surface, current_data):
    font = pygame.font.Font(None, 14)
    info_text = [
        f"Time: {current_data['Time [s]']:.2f} s",
        f"Altitude: {current_data['Smoothed altitude [km]']:.2f} km",
        f"Speed: {current_data['Smoothed speed [m/s]']:.2f} m/s",
        f"Mach: {current_data['Mach number']:.2f}",
        f"Dynamic Pressure: {current_data['Dynamic pressure [kPa]']:.2f} kPa"
    ]
    for i, text in enumerate(info_text):
        text_surface = font.render(text, True, BLACK)
        surface.blit(text_surface, (10, 10 + i * 30))
def draw_axis_labels(surface):
    font = pygame.font.Font(None, 24)
    
    # Título
    title = font.render("Trajectory profile", True, BLACK)
    surface.blit(title, (width // 2 - title.get_width() // 2, 10))
    
    # Eixo X
    x_label = font.render("Downrange distance [km]", True, BLACK)
    surface.blit(x_label, (width // 2 - x_label.get_width() // 2, height - 30))
    
    # Eixo Y
    y_label = font.render("Altitude [km]", True, BLACK)
    y_label = pygame.transform.rotate(y_label, 90)
    surface.blit(y_label, (10, height // 2 - y_label.get_height() // 2))

def draw_full_trajectory(surface, data, max_altitude, max_downrange):
    trajectory_points = []
    for point in data:
        x = map_value(point['Downrange distance [km]'], 0, max_downrange, width * 0.1, width * 0.9)
        y = map_value(point['Smoothed altitude [km]'], 0, max_altitude, height * 0.9, height * 0.1)
        trajectory_points.append((int(x), int(y)))
    
    if len(trajectory_points) > 1:
        # Draw anti-aliased lines
        for i in range(len(trajectory_points) - 1):
            pygame.gfxdraw.line(surface, 
                                int(trajectory_points[i][0]), int(trajectory_points[i][1]),
                                int(trajectory_points[i+1][0]), int(trajectory_points[i+1][1]),
                                BLUE)
        
        # Optionally, draw anti-aliased circles at each point for smoother appearance
        for point in trajectory_points:
            pygame.gfxdraw.aacircle(surface, int(point[0]), int(point[1]), 1, BLUE)
            pygame.gfxdraw.filled_circle(surface, int(point[0]), int(point[1]), 1, BLUE)
    
    draw_trajectory_points(surface, data, max_altitude, max_downrange)
    draw_trajectory_events(surface, data, max_altitude, max_downrange)

# Função para calcular a posição do topo do foguete
def calculate_top_position(pos_x, pos_y, angle, rocket_height, time):
    if is_rocket_inverted(time):
        angle += -90  # Inverte o ângulo se o foguete estiver de cabeça para baixo
    
    angle_rad = math.radians(angle)
    top_x = pos_x + rocket_height * math.sin(angle_rad)
    top_y = pos_y - rocket_height * math.cos(angle_rad)
    return top_x, top_y

# Loop principal
running = True
clock = pygame.time.Clock()
frame = 0
max_altitude = max(d['Smoothed altitude [km]'] for d in data)
max_downrange = max(d['Downrange distance [km]'] for d in data)

# Criar uma superfície para a trajetória
trajectory_surface = pygame.Surface((width, height), pygame.SRCALPHA)
draw_full_trajectory(trajectory_surface, data, max_altitude, max_downrange)

rocket_height = svg_height * scale  # Altura do foguete na escala da tela

while running and frame < len(data):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Desenhar a trajetória completa
    screen.blit(trajectory_surface, (0, 0))

    current_data = data[frame]

    screen.blit(trajectory_surface, (0, 0))

    draw_axis_labels(screen)

    current_data = data[frame]
    current_time = current_data['Time [s]']

    # Mapear dados para a tela
    pos_x = map_value(current_data['Downrange distance [km]'], 0, max_downrange, width * 0.1, width * 0.9)
    pos_y = map_value(current_data['Smoothed altitude [km]'], 0, max_altitude, height * 0.9, height * 0.1)
    
    
    # Calcular ângulo baseado na velocidade horizontal e vertical
    angle = math.degrees(math.atan2(-current_data['Vertical speed [m/s]'], current_data['Horizontal speed [m/s]']))
    if svg_orientation == "inverted":
        angle += 180

    # Calcular a posição do topo do foguete
    top_x, top_y = calculate_top_position(pos_x, pos_y, angle, rocket_height, current_time)


    # Desenhar o SVG rotacionado e posicionado
    draw_svg(drawing_surface, paths, angle, pos_x, pos_y, current_time)
    screen.blit(drawing_surface, (0, 0))


    # Desenhar partículas de fogo
    draw_fire_particles(screen, pos_x, pos_y, angle, current_data['Smoothed speed [m/s]'], current_time)


    # Desenhar o ponto atual na trajetória (agora no topo do foguete)
    pygame.draw.circle(screen, RED, (int(top_x), int(top_y)), 5)

    # Desenhar informações
    draw_info(screen, current_data)

    # Desenhar linha do solo
    pygame.draw.line(screen, BLACK, (0, height - 10), (width, height - 10), 1)

    # Controle da espessura da linha
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and TRAJECTORY_LINE_THICKNESS < 10:
        TRAJECTORY_LINE_THICKNESS += 1
        trajectory_surface.fill((0, 0, 0, 0))  # Limpar a superfície
        draw_full_trajectory(trajectory_surface, data, max_altitude, max_downrange)
    elif keys[pygame.K_DOWN] and TRAJECTORY_LINE_THICKNESS > 1:
        TRAJECTORY_LINE_THICKNESS -= 1
        trajectory_surface.fill((0, 0, 0, 0))  # Limpar a superfície
        draw_full_trajectory(trajectory_surface, data, max_altitude, max_downrange)

    pygame.display.flip()

    frame += 1
    clock.tick(20)  # Ajuste este valor para controlar a velocidade da simulação

pygame.quit()