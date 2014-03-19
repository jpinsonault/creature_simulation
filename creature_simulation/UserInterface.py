from Colors import *
import pygame

class TextBox(object):
    """Responsible for single line text boxes"""
    def __init__(self, text, position, size=22, color=WHITE, bold=False, italic=False, typeface="monospace"):
        super(TextBox, self).__init__()
        self.text = text
        self.position = position
        self.size = size
        self.bold = bold
        self.italic = italic
        self.color = color

        self.font = pygame.font.SysFont(typeface, size)
        self.font.set_bold(bold)
        self.font.set_italic(italic)

        self.label = None
        self.make_label()

    def set(self, new_string):
        self.text = new_string
        self.make_label()

    def make_label(self):
        self.label = self.font.render(self.text, 1, self.color) 
        
    def draw(self, screen):
        screen.blit(self.label, self.position)


class MultilineTextBox(TextBox):
    """Takes a list of strings and draws them with spacing between each line"""
    def __init__(self, text, position, size=22, color=WHITE, bold=False, italic=False, typeface="monospace"):
        self.labels = None
        super(MultilineTextBox, self).__init__(text, position, size, color, bold, italic, typeface)

    def make_label(self):
        x, y = self.position

        self.labels = [self.font.render(line, 1, self.color) for line in self.text]

    def draw(self, screen):
        x, y = self.position
        for label in self.labels:
            screen.blit(label, (x, y))
            y += self.font.get_linesize()


class UserInterface(object):
    """Handles drawing text on the screen each frame"""
    def __init__(self, screen):
        super(UserInterface, self).__init__()
        self.screen = screen

        self.elements = []

    def draw(self):
        """Draws all the UI objects on the screen"""

        for element in self.elements:
            element.draw(self.screen)

    def add(self, new_element):
        self.elements.append(new_element)

    def remove(self, remove_object):
        self.elements.remove(remove_object)