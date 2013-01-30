Week 4 - Breakout Redux
=======================

Revisit https://github.com/oc-cs170/breakout.git and implement new skills.

To-do
-----

1. Implement Ball, Paddle, and Brick as Sprites.
2. Use Rect objects and pygame collisions.
3. Use sprite groups to manage game objects.
4. Implement scoring.
5. Implement on-screen display (OSD) of game's text information.
6. Implement levels so new walls of bricks can be drawn after old are cleared.
7. Implement "Super Bricks" that have a different appearance and take 3 hits to destroy.

Notes
-----

Classes that inherit from Sprite need to be set up, as follows:

```python
class NewThing(pygame.sprite.Sprite):
	def __init__(self):
	    # Call __init__ from Sprite
	    pygame.sprite.Sprite.__init__(self)

		# Insert your code here
		# self.image - MUST BE DEFINED
		# self.rect  - MUST BE DEFINED
```
