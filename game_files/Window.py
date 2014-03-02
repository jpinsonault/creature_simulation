from GraphNode import GraphNode

class Window(GraphNode):
    """
    Hold properties and methods for dealing with zooming and moving the screen

    Treats it's own x,y coordinate as the center of the screen to enable correct 
        zooming
    """
    MIN_ZOOM = 0.01
    MAX_ZOOM = 4.0

    def __init__(self, width, height, x=0, y=0, zoom = 1.0, zoom_speed = 0.001):
        super(Window, self).__init__(x=x, y=y)

        self.width = width
        self.height = height
        # Zoom is a factor, 1.0 being no zoom, 2.0 being twice as many pixels on each axis
        self.zoom = float(zoom)
        self.zoom_speed = zoom_speed
        

    def zoom_in(self, dt):
        self.zoom += dt * self.zoom_speed
        self.zoom = max(self.zoom, self.MIN_ZOOM)
        self.zoom = min(self.zoom, self.MAX_ZOOM)

    def zoom_out(self, dt):
        self.zoom -= dt * self.zoom_speed
        self.zoom = max(self.zoom, self.MIN_ZOOM)
        self.zoom = min(self.zoom, self.MAX_ZOOM)

    def scale(self, point):
        """Scales a coordinate from the virtual world to the screen"""
        x = (point[0] + self.x) / self.zoom + self.width/2
        y = (point[1] + self.y) / self.zoom + self.height/2
        return [x, y]

    def on_screen(self, point):
        """Returns true if the point intersects the screen"""
        screen_coord = self.scale(point)

        return (screen_coord[0] >= 0 and screen_coord[1] >= 0 and
            screen_coord[0] < self.width and screen_coord[1] < self.height)
