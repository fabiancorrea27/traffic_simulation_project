import pygame
from config import GREEN, WINDOW_WIDTH, WINDOW_HEIGHT
from ui.display import draw_scene
from simulation import Intersection, Vehicle


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Simulación de Intersección")
    clock = pygame.time.Clock()
    running = True

    intersection = Intersection()
    intersection.add_vehicles(2, "S")
    intersection.add_vehicles(2, "N")
    intersection.add_vehicles(2, "E")
    intersection.add_vehicles(2, "W")
    

    
    toggle_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Alternar semáforos cada 120 frames (~2 segundos a 60fps)
        toggle_timer += 1
        if toggle_timer >= 120:
            intersection.change_lights()
            toggle_timer = 0
        intersection.update()

        draw_scene(screen, intersection)
        pygame.display.flip()
        clock.tick(120)

    pygame.quit()


if __name__ == "__main__":
    main()
