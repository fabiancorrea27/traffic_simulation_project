import pygame
from config import *

def draw_scene(screen, intersection):
    # Fondo gris claro
    screen.fill(WHITE)

    # Dibujar calles como cruces
    center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    pygame.draw.rect(screen, GRAY, (center[0] - ROAD_WIDTH//2, 0, ROAD_WIDTH, WINDOW_HEIGHT))  # Vertical
    pygame.draw.rect(screen, GRAY, (0, center[1] - ROAD_WIDTH//2, WINDOW_WIDTH, ROAD_WIDTH))  # Horizontal

    # Dibujar semáforos
    for light in intersection.traffic_lights.values():
        color = light.state
        pygame.draw.circle(screen, color, light.position, LIGHT_RADIUS)

    # Dibujar vehículos
    intersection.draw(screen)
