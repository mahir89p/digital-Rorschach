from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Ellipse, Color
from kivy.config import Config
from math import sqrt

Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')

sensor_radius = 2
grid_size = 100
rect_size = 100
sensor_spacing = rect_size / grid_size

class MyWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.red_grid_pos = (50, 250)
        self.white_grid_positions = [
            (300, 350),  # Top-left
            (400, 350),  # Top-right (flip columns)
            (300, 250),  # Bottom-left (flip rows)
            (400, 250),  # Bottom-right (flip both)
        ]

        self.red_sensor_positions = []
        self.red_sensors = []
        self.white_sensor_positions_list = [[], [], [], []]
        self.white_dots_grids = [[], [], [], []]
        self.last_drawn_cells = set()

        with self.canvas:
            # Draw red grid
            Color(1, 1, 1)
            Rectangle(pos=self.red_grid_pos, size=(rect_size, rect_size))

            Color(1, 0, 0)
            for row in range(grid_size):
                for col in range(grid_size):
                    x = self.red_grid_pos[0] + col * sensor_spacing + sensor_spacing / 2
                    y = self.red_grid_pos[1] + row * sensor_spacing + sensor_spacing / 2
                    self.red_sensor_positions.append((x, y))
                    ellipse = Ellipse(pos=(x - sensor_radius, y - sensor_radius), size=(sensor_radius * 2, sensor_radius * 2))
                    self.red_sensors.append(ellipse)

            # Draw all 4 white grids
            for i, (x0, y0) in enumerate(self.white_grid_positions):
                Color(1, 1, 1)
                Rectangle(pos=(x0, y0), size=(rect_size, rect_size))
                dots = []
                positions = []
                for row in range(grid_size):
                    for col in range(grid_size):
                        flip_col = (i == 1 or i == 3)
                        flip_row = (i == 2 or i == 3)

                        actual_col = grid_size - 1 - col if flip_col else col
                        actual_row = grid_size - 1 - row if flip_row else row

                        x = x0 + col * sensor_spacing + sensor_spacing / 2
                        y = y0 + row * sensor_spacing + sensor_spacing / 2
                        positions.append((x, y))
                        ellipse = Ellipse(
                            pos=(x - sensor_radius, y - sensor_radius),
                            size=(sensor_radius * 2, sensor_radius * 2)
                        )
                        dots.append(ellipse)
                self.white_sensor_positions_list[i] = positions
                self.white_dots_grids[i] = dots

        self.is_pressed = False

    def paint_dot(self, row, col):
        if (row, col) in self.last_drawn_cells:
            return
        self.last_drawn_cells.add((row, col))

        with self.canvas:
            for i in range(4):
                flip_col = (i == 1 or i == 3)
                flip_row = (i == 2 or i == 3)

                actual_col = grid_size - 1 - col if flip_col else col
                actual_row = grid_size - 1 - row if flip_row else row
                actual_idx = actual_row * grid_size + actual_col

                self.white_dots_grids[i][actual_idx].size = (0, 0)
                x, y = self.white_sensor_positions_list[i][actual_idx]
                Color(1, 0, 0)
                Ellipse(pos=(x - sensor_radius, y - sensor_radius), size=(sensor_radius * 2, sensor_radius * 2))

    def process_touch(self, touch):
        x0, y0 = self.red_grid_pos
        if x0 <= touch.x <= x0 + rect_size and y0 <= touch.y <= y0 + rect_size:
            col = min(grid_size - 1, max(0, int((touch.x - x0) / sensor_spacing)))
            row = min(grid_size - 1, max(0, int((touch.y - y0) / sensor_spacing)))
            sensor_x = x0 + col * sensor_spacing + sensor_spacing / 2
            sensor_y = y0 + row * sensor_spacing + sensor_spacing / 2
            dx = touch.x - sensor_x
            dy = touch.y - sensor_y
            if sqrt(dx*dx + dy*dy) <= sensor_radius:
                print(f"Drawing on ({row+1}, {col+1})")
                self.paint_dot(row, col)

    def on_touch_down(self, touch):
        if touch.button == 'left':
            self.last_drawn_cells.clear()
            self.is_pressed = True
            self.process_touch(touch)

    def on_touch_move(self, touch):
        if self.is_pressed:
            self.process_touch(touch)

    def on_touch_up(self, touch):
        if touch.button == 'left':
            self.is_pressed = False

class MyApp(App):
    def build(self):
        return MyWidget()

if __name__ == '__main__':
    MyApp().run()
