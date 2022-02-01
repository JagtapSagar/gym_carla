import numpy as np
import pygame
from pygame.locals import KMOD_CTRL
from pygame.locals import KMOD_SHIFT
from pygame.locals import K_0
from pygame.locals import K_9
from pygame.locals import K_BACKQUOTE
from pygame.locals import K_BACKSPACE
from pygame.locals import K_COMMA
from pygame.locals import K_DOWN
from pygame.locals import K_ESCAPE
from pygame.locals import K_F1
from pygame.locals import K_LEFT
from pygame.locals import K_PERIOD
from pygame.locals import K_RIGHT
from pygame.locals import K_SLASH
from pygame.locals import K_SPACE
from pygame.locals import K_TAB
from pygame.locals import K_UP
from pygame.locals import K_a
from pygame.locals import K_b
from pygame.locals import K_c
from pygame.locals import K_d
from pygame.locals import K_g
from pygame.locals import K_h
from pygame.locals import K_i
from pygame.locals import K_l
from pygame.locals import K_m
from pygame.locals import K_n
from pygame.locals import K_p
from pygame.locals import K_q
from pygame.locals import K_r
from pygame.locals import K_s
from pygame.locals import K_v
from pygame.locals import K_w
from pygame.locals import K_x
from pygame.locals import K_z
from pygame.locals import K_MINUS
from pygame.locals import K_EQUALS

class Pygame_2d:
    def __init__(self, im_width, im_height):
        # Initialize pygame environment
        pygame.init()
        self.display = pygame.display.set_mode((im_width, im_height))
        pygame.display.set_caption("gym_pygame")
        self.clock = pygame.time.Clock()

        # Fill pygame window with black background
        self.display.fill((0,0,0))
        pygame.display.flip()

        # TOGGLES
        self.quit            = False
        self.manual          = False       # To enable manual control
        self.autopilot       = False       # To set autopilot for immitation

    def to_quit(self):
        """Check if pygame window terminated"""
        return self.quit
    
    def set_autopilot(self):
        """Returns true if autopilot toggle enabled"""
        return self.autopilot
    
    def get_actions(self, action_space):
        """Returns manual actions to execute"""
        # Zero placeholder value
        action = np.zeros(action_space.shape)      # not sure if .shape works with gym.spaces.Discrete
        return action
    
    def render(self,image):
        self.clock.tick()
        self.display.fill((0,0,0))
        surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
        self.display.blit(surface, (0,0))
        pygame.display.flip()          # Update display/game window
    
    def event_parser(self):
        # This is event parser module

        # TODO
        # Add manual control toggle
        #            - seperate keys to enable or disable
        #            - disable autopilot toggle if this is enabled
        # Add autopilot toggle
        #            - seperate keys to enable or disable
        #            - disable manual control if this is enabled
        # Add manual control events
        # Add events to change sensor value being displayed

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.quit = True
                pygame.quit()
