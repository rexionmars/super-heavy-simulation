import pygame
from simulation import Simulation
from renderer import Renderer
from data_loader import DataLoader

def main():
    pygame.init()
    width, height = 1000, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Super Heavy Atmospheric Reentry - Real Data Simulation")

    data_loader = DataLoader('/home/luisgoc/workspace/super-heavy-simulation/assets/data/IFT3_full_data_booster.csv')
    simulation = Simulation(data_loader.load_data())
    renderer = Renderer(screen, width, height)

    running = True
    clock = pygame.time.Clock()

    while running and not simulation.is_finished():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        simulation.update()
        renderer.render(simulation)

        pygame.display.flip()
        clock.tick(60)  # Increase to 60 FPS for smoother animation

    pygame.quit()

if __name__ == "__main__":
    main()