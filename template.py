#!/usr/bin/env python

"""Main file with game loop for PyGame.
"""

import pygame

WINDOW_TITLE = 'PyGame'
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30


class PyGame(object):
    """Create a game of PyGame."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Use a clock to control frame rate
        self.clock = pygame.time.Clock()

    def play(self):
        """Start PyGame program.
        """

        running = True
        while running:
            self.clock.tick(FPS)  # Max frames per second

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    running = False

            # Draw the scene
            self.screen.fill((0, 0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    game = PyGame()
    game.play()
