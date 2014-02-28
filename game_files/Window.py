from GraphNode import GraphNode

class Window(GraphNode):
    """
    Hold properties and methods for dealing with zooming and moving the screen

    Treats it's own x,y coordinate as the center of the screen to enable correct 
    	zooming
    """
    MIN_ZOOM = 0.01
    MAX_ZOOM = 4.0

    def __init__(self, width, height, zoom = 1.0):
		super(Window, self).__init__()

        self.width = width
        self.height = height
        # Zoom is a factor, 1.0 being no zoom, 2.0 being twice as many pixels on each axis
        self.zoom = float(zoom)
        

    def set_zoom(self, zoom):
        self.zoom += zoom
        self.zoom = max(self.zoom, self.MIN_ZOOM)
        self.zoom = min(self.zoom, self.MAX_ZOOM)

    def scale(self, coord):
        """Scales a coordinate from the virtual world to the screen"""
        x = int((coord[0] + self.x) / self.zoom + self.width/2)
        y = int((coord[1] + self.y) / self.zoom + self.height/2)
        return [x, y]
