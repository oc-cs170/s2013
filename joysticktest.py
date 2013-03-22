#!/usr/bin/env python

"""Main file with game loop for JoystickTest.
"""

import pygame

WINDOW_TITLE = 'JoystickTest'
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 30


class JoystickTest(object):
    """Create a game of JoystickTest."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Use a clock to control frame rate
        self.clock = pygame.time.Clock()

    def play(self):
        """Start JoystickTest program.
        """
        # Player 1 Joystick
        j1 = pygame.joystick.Joystick(0)
        j1.init()

        # Player 2 Joystick
        j2 = pygame.joystick.Joystick(1)
        j2.init()

        running = True
        while running:
            self.clock.tick(FPS)  # Max frames per second

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Quit when user tries to close window
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    # Quit when user hits 'Q' key
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Quit when user hits 'Esc' key
                    running = False

                # Get joystick button events
                if event.type == pygame.JOYBUTTONDOWN:
                    print event.joy, event.button

                # Get joystick d-pad events
                if event.type == pygame.JOYHATMOTION:
                    print event.joy, event.hat, event.value

                # Get joystick analog events
                if event.type == pygame.JOYAXISMOTION:
                    print event.joy, event.axis, event.value

            # Draw the scene
            self.screen.fill((0, 0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    game = JoystickTest()
    game.play()
