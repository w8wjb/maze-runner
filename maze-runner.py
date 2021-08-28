#!/usr/bin/env python3
from collections import deque as queue
import requests
import sys
import tkinter
from tkinter import ttk
from PIL import Image



class BrenttMap:
    MAZE_LEVEL_BASE_URL = "https://brentts-maze-runner.herokuapp.com//mazerunner/"

    def __init__(self):
        self.level = '1'

    def get_start(self):
        return Room(0, 0, rtype="@", path=tuple())

    def get_levels(self):
        return ('1', '2', '3', '4', '5', '6', '7')

    def set_level(self, level):
        self.level = level

    def check_path(self, path):
        url = BrenttMap.MAZE_LEVEL_BASE_URL + self.level

        for retry in range(3):
            try:
                # print(url, path)
                response = requests.put(url, json=path)
                return response.text
            except ConnectionResetError:
                print("Connection reset, retrying")
                continue
        print("Connection failed")
            

class PNGMap:
    def __init__(self, image_path, wall_width=2, room_width=14):
        self.image_path = image_path
        self.wall_width = wall_width
        self.room_width = room_width
        self.wall_middle = self.wall_width + (self.room_width / 2)
        self.cell_size = room_width + wall_width
        self.start = None
   
    def get_start(self):
        if self.start:
            return self.start
        
        y = 0
        x = 0
        img_x = 0
        # walk along the top of the map and find the entry point
        while img_x < self.max_size[0]:
            walls = self.get_walls((x, y))
            if not walls[0]:
                self.start = Room(x, y, rtype="@", path=tuple())
                return self.start
            x += 1
            img_x += self.cell_size

        self.start = Room(0, 0, rtype="@", path=tuple())
        return self.start

    def get_levels(self):
        return ("/Users/wbustraa/Downloads/20 by 20 orthogonal maze.png",
        "/Users/wbustraa/Downloads/40 by 20 orthogonal maze.png")

    def set_level(self, level):
        self.level = level
        self.image = Image.open(self.level).convert('L') # L == Luma
        self.max_size = self.image.size

    def in_bounds(self, xy):
        if xy[0] < 0 \
            or xy[0] > self.max_size[0] \
            or xy[1] < 0 \
            or xy[1] > self.max_size[1]:
            return False
        return True


    def get_walls(self, roomxy):

        rx, ry = roomxy
        cell_x1 = self.cell_size * rx
        cell_y1 = self.cell_size * ry

        if not self.in_bounds((cell_x1, cell_y1)):
            return (True, True, True, True)

        ny = cell_y1
        ex = cell_x1 + self.wall_width + self.room_width
        wx = cell_x1
        sy = cell_y1 + self.wall_width + self.room_width

        if ny < 0:
            wall_n = True
        else:
            n = (wx + self.wall_middle, ny)
            if self.in_bounds(n):
                wall_n = self.image.getpixel(n) < 128
            else:
                wall_n = None

        if ex > self.max_size[0]:
            wall_e = True
        else:
            e = (ex, ny + self.wall_middle)
            if self.in_bounds(e):
                wall_e = self.image.getpixel(e) < 128
            else:
                wall_e = None

        if wx < 0:
            wall_w = True
        else:
            w = (wx, ny + self.wall_middle)
            if self.in_bounds(w):
                wall_w = self.image.getpixel(w) < 128
            else:
                wall_w = None

        if sy > self.max_size[1]:
            wall_s = True
        else:
            s = (wx + self.wall_middle, sy)
            if self.in_bounds(s):
                wall_s = self.image.getpixel(s) < 128
            else:
                wall_s = None

        return (wall_n, wall_e, wall_w, wall_s)

    def check_path(self, path):
        room = (self.start.x, self.start.y)
        for d in path:
            if d == "N":
                walls = self.get_walls(room)
                if walls[0] is None:
                    return "Exit"
                if walls[0]:
                    return "Wall"
                room = (room[0], room[1] - 1)
            elif d == "E":
                walls = self.get_walls(room)
                if walls[1] is None:
                    return "Exit"
                if walls[1]:
                    return "Wall"
                room = (room[0] + 1, room[1])
            elif d == "W":
                walls = self.get_walls(room)
                if walls[2] is None:
                    return "Exit"
                if walls[2]:
                    return "Wall"
                room = (room[0] - 1, room[1])
            elif d == "S":
                walls = self.get_walls(room)
                if walls[3] is None:
                    return "Exit"
                if walls[3]:
                    return "Wall"
                room = (room[0], room[1] + 1)
        return "Open Space"

class Room:
    def __init__(self, x: int, y: int, rtype = "_", path: tuple = ()):
        super().__init__()
        self.x = x
        self.y = y
        self.rtype = rtype
        self.walls = {"N": None, "E": None, "W": None, "S": None}
        self.path = path

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.x == other.x and self.y == other.y

    def neighbor(self, direction):
        new_path = self.path + (direction,)
        if direction == "N":
            return Room(self.x, self.y - 1, path=new_path)
        elif direction == "NE":            
            return Room(self.x + 1, self.y - 1, path=new_path)
        elif direction == "E":
            return Room(self.x + 1, self.y, path=new_path)
        elif direction == "SE":
            return Room(self.x + 1, self.y + 1, path=new_path)
        elif direction == "S":
            return Room(self.x, self.y + 1, path=new_path)
        elif direction == "SW":
            return Room(self.x - 1, self.y + 1, path=new_path)
        elif direction == "W":
            return Room(self.x - 1, self.y, path=new_path)
        elif direction == "NW":
            return Room(self.x - 1, self.y - 1, path=new_path)
        else:
            return None
            



class MazeRunner:
    def __init__(self, map, scale = 20):
        self.map = map
        self.scale = scale
        self.level = '1'
        self.dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        self.arrows = {'N': 90,
        'NE': 45,
        'E': 0,
        'SE': -45,
        'S': -90,
        'SW': -135,
        'W': -180,
        'NW': -225}



    def show(self):
        self.root = tkinter.Tk()
        self.root.title('Maze Runner')
        self.canvas = tkinter.Canvas(self.root, bg="grey", height=500, width=1000)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.btn_frame = ttk.Frame(self.root)

        levels = self.map.get_levels()
        self.level_chooser = ttk.Combobox(self.btn_frame, width=2, textvariable=self.level, value=levels, state='readonly')
        self.level_chooser.current(0)
        self.level_chooser.pack(side = tkinter.LEFT, padx=10)

        self.button = tkinter.Button(self.btn_frame, text="Start", command=self.start_mapping)
        self.button.pack(side = tkinter.LEFT)

        self.btn_frame.pack()

        self.root.update_idletasks()
        self.root.update()

        self.root.mainloop()

    def breadth_first_search(self, level):

        q = queue()

        start = self.map.get_start()
        q.append(start)

        visited = set()

        exits = []

        shortest_found = False

        while q:
            room = q.popleft()

            visited.add(room)

            for d in self.dirs:
                neighbor = room.neighbor(d)

                if neighbor in visited:
                    continue

                valid = self.map.check_path(neighbor.path)

                if valid == "Open Space":
                    room.walls[d] = False
                    q.append(neighbor)
                elif valid == "Wall":
                    room.walls[d] = True
                    continue
                else:
                    room.rtype = "X"
                    print(valid)
                    exits.append(neighbor.path)

                    if not shortest_found:
                        shortest_found = True

                        last = start
                        for step in neighbor.path[:-1]:
                            if last.x == 0 and last.y == 0:
                                last = last.neighbor(step)
                                continue
                            last.rtype = step
                            self.draw_room(last)
                            last = last.neighbor(step)


            self.draw_room(room)

        return exits

    def draw_room(self, room):
        tlx = room.x * self.scale
        tly = room.y * self.scale
        brx = tlx + self.scale
        bry = tly + self.scale

        self.canvas.width = 600

        if room.rtype == "@":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="green")
        elif room.rtype == "#":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="black")
        elif room.rtype == "X":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="red", outline="")
        elif room.rtype in self.dirs:
            self.canvas.create_oval(tlx+1, tly+1, brx-2, bry-2, fill="SpringGreen3", outline="")
            angle = self.arrows[room.rtype]
            self.canvas.create_text(tlx+10, tly+10, text="➤", angle=angle, fill="dark green", font=("Helvetica", 12))
        else:
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="white", outline="")
            
            if room.walls['N']:
                self.canvas.create_line(tlx, tly, brx, tly, width=2)
            if room.walls['E']:
                self.canvas.create_line(brx, tly, brx, bry, width=2)
            if room.walls['W']:
                self.canvas.create_line(tlx, tly, tlx, bry, width=2)
            if room.walls['S']:
                self.canvas.create_line(tlx, bry, brx, bry, width=2)

        
        self.canvas.update_idletasks()
        self.canvas.update()

    def start_mapping(self):
        self.canvas.delete("all")
        level = self.level_chooser.get()
        self.map.set_level(level)
        result = self.breadth_first_search(level)
        print(f"Level {level} ", result)    

def main(argv):
    #map = PNGMap("/Users/wbustraa/Downloads/40 by 20 orthogonal maze.png")
    map = BrenttMap()
    runner = MazeRunner(map)
    runner.show()

if __name__ == "__main__":
    main(sys.argv[1:])