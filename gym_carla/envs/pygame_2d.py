try:
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
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

class Pygame_2d:
    def __init__(self, im_width, im_height):
        pygame.init()
        self.display = pygame.display.set_mode((im_width, im_height))
        pygame.display.set_caption("gym_pygame")
        self.display.fill((0,0,0))
        pygame.display.flip()
        self.clock = pygame.time.Clock()

        self.quit = False
        self.manual = False
    
    def render(self,image):
        self.clock.tick()
        self.display.fill((0,0,0))
        surface = pygame.surfarray.make_surface(image.swapaxes(0, 1))
        self.display.blit(surface, (0,0))
        pygame.display.flip()          # Update display/game window
    
    def to_quit(self):
        """Check if pygame window terminated"""
        return self.quit
    
    def get_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.quit = True
                pygame.quit()
