Week 7 - Games Cleanup
======================

Revisit the previous projects and update them to improve their flow and presentation.

To-do
-----

1. Add sounds and music
2. Add game start/splash screen
3. Display score as text on-screen
4. Display remaining lives as text or picture on-screen
5. Implement multiple rounds (after board cleared)
6. Implement pauses between rounds
7. Make sure that users can always view the state of the game
8. Add quit confirms
9. Add game over/play again screen
10. Fix any existing glitches or inconsistencies

Notes
-----

* A nice online wav file resource is http://www.soundbyter.com.
* There are three steps to adding sound to your pygames
 * Initialize the mixer
 * Load the sound from file
 * Play the sound when appropriate


```python
class SomeGame(object):
    def __init__(self):
        # Must call pygame.mixer.pre_init before pygame.init
        pygame.mixer.pre_init(11025, -16, 2, 1024)
        pygame.init()



        # Loading a sound from a local file
        self.some_sound = pygame.mixer.Sound('some_file.wav')



        # Playing a sound
        self.some_sound.play()
```
