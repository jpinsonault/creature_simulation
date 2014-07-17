from Colors import *
import pygame
from time import time

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

    def clear(self):
        self.text = ""
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

    def clear(self):
        self.text = [""]
        self.make_label()

    def draw(self, screen):
        x, y = self.position
        for label in self.labels:
            screen.blit(label, (x, y))
            y += self.font.get_linesize()


class Toast(object):
    """A temporary string that goes away"""
    def __init__(self, message, timeout=1.0, textbox=None):
        super(Toast, self).__init__()
        self.message = message
        self.timeout = timeout

        self.textbox = textbox

        self.creation_time = None

    def done(self):
        """Returns true if the toast is done"""

        # Initalize the creation_time if this is the first time done()
        #   is called
        if not self.creation_time:
            self.creation_time = time()
        return time() - self.creation_time >= self.timeout
        

class UserInterface(object):
    """Handles drawing text on the screen each frame"""
    def __init__(self, screen):
        super(UserInterface, self).__init__()
        self.screen = screen

        self.elements = []

        self.toasts = []

    def draw(self):
        """Draws all the UI objects on the screen"""

        toast = self._next_toast()

        if toast:
            toast.textbox.draw(self.screen)

        for element in self.elements:
            element.draw(self.screen)

    def add(self, new_element):
        self.elements.append(new_element)

    def remove(self, remove_object):
        self.elements.remove(remove_object)

    def toast(self, message):
        x = self.screen.get_width() / 2
        y = 40
        new_toast = Toast(message, textbox=toast_textbox)

        toast_textbox = TextBox(message, (x, y), size=30)

        self.toasts.append(new_toast)

    def _next_toast(self):
        if self.toasts:
            toast = self.toasts[0]

            if not toast.done():
                return toast
            else:
                self.toasts.remove(toast)
                return self._next_toast()

        return None