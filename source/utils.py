import math

def map_value(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

def rotate_point(x, y, cx, cy, angle):
    rad = math.radians(angle)
    dx = x - cx
    dy = y - cy
    rotated_x = cx + dx * math.cos(rad) - dy * math.sin(rad)
    rotated_y = cy + dx * math.sin(rad) + dy * math.cos(rad)
    return rotated_x, rotated_y

def calculate_top_position(pos_x, pos_y, angle, rocket_height, time):
    if is_rocket_inverted(time):
        angle += 0  # Inverte o ângulo se o foguete estiver de cabeça para baixo
    
    angle_rad = math.radians(angle)
    top_x = pos_x + rocket_height * math.sin(angle_rad)
    top_y = pos_y - rocket_height * math.cos(angle_rad)
    return top_x, top_y

def is_rocket_inverted(time):
    stage_separation_time = 60*2 + 48  # Tempo da separação dos estágios
    return time > stage_separation_time