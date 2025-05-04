import pygame
from config import GREEN, WINDOW_WIDTH, WINDOW_HEIGHT, RED, YELLOW
from ui.display import draw_scene
from simulation import Intersection, Vehicle


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simulación de Intersección")
    clock = pygame.time.Clock()
    running = True

    intersection = Intersection()
    intersection.add_vehicle(Vehicle("N"))
    intersection.add_vehicle(Vehicle("S"))
    intersection.add_vehicle(Vehicle("E"))
    intersection.add_vehicle(Vehicle("W"))

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
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
