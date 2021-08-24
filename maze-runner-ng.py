#!/usr/bin/env python3
from collections import deque as queue
import requests
import sys
import tkinter
from PIL import Image

# LEVEL = 4
MAZE_LEVEL_BASE_URL = "https://brentts-maze-runner.herokuapp.com//mazerunner/"

m = 100
n = 100
scale = 20

class Map:
    def __init__(self, image_path, start, wall_width=2, room_width=14):
        self.image_path = image_path
        self.start = start
        self.wall_width = wall_width
        self.room_width = room_width
        self.wall_middle = self.wall_width + (self.room_width / 2)
        self.cell_size = room_width + wall_width
        self.image = Image.open(image_path).convert('L') # L == Luma
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
        room = self.start
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

    def neighbor(self, direction):
        if direction == "N":
            return Room(self.x, self.y - 1, path = self.path + (direction,) )
        elif direction == "E":
            return Room(self.x + 1, self.y, path = self.path + (direction,) )
        elif direction == "W":
            return Room(self.x - 1, self.y, path = self.path + (direction,) )
        else:
            return Room(self.x, self.y + 1, path = self.path + (direction,) )

    # def check_path(self, level):
    #     url = MAZE_LEVEL_BASE_URL + str(level)
    #     response = requests.put(url, json=self.path)
    #     return response.text

    # def check_path(self, level):
    #     global map
    #     return map.check_path(self.path)


    

class MazeRunner:
    def __init__(self, image_path):
        self.map = Map(image_path, (0,0))


    def run(self):
        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.root, bg="white", height=300, width=300)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.button = tkinter.Button(self.root, text="Start", command=self.start_mapping)
        self.button.pack()
        self.root.update_idletasks()
        self.root.update()

        self.root.mainloop()

    def breadth_first_search(self, level):

        q = queue()

        start = Room(0, 0, rtype="@", path=tuple())
        q.append(start)

        visited = [[None for x in range(n)] for x in range(m)]

        exits = []

        shortest_found = False

        room_count = 0
        while q:
            room = q.popleft()

            visited[room.x][room.y] = room

            dirs = ["N", "E", "W", "S"]

            for d in dirs:
                neighbor = room.neighbor(d)

                if visited[neighbor.x][neighbor.y]:
                    continue

                valid = self.map.check_path(neighbor.path)
                # valid = neighbor.check_path(level)

                if valid == "Open Space":
                    room.walls[d] = False
                    q.append(neighbor)
                elif valid == "Wall":
                    room.walls[d] = True
                    # visited[neighbor.x][neighbor.y] = "#"
                    # draw_room(canvas, neighbor, "#")
                    continue
                else:
                    room.rtype = "X"
                    # draw_room(canvas, neighbor, "X")
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



                    # return neighbor.path

            # print((room.x, room.y, room.walls))


            self.draw_room(room)
            room_count += 1
            # if room_count >= 50:
            #     break

        return exits
    def draw_room(self, room):
        tlx = room.x * scale
        tly = room.y * scale
        brx = tlx + scale
        bry = tly + scale

        self.canvas.width = 600

        if room.rtype == "@":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="green")
        elif room.rtype == "#":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="black")
        elif room.rtype == "X":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="red", outline="")
        elif room.rtype == "N":
            self.canvas.create_oval(tlx+1, tly+1, brx-2, bry-2, fill="SpringGreen3", outline="")
            self.canvas.create_text(tlx+10, tly+10, text="▲", fill="dark green", font=("Helvetica", 12))
        elif room.rtype == "E":
            self.canvas.create_oval(tlx+1, tly+1, brx-2, bry-2, fill="SpringGreen3", outline="")
            self.canvas.create_text(tlx+10, tly+10, text="▶", fill="dark green", font=("Helvetica", 12))
        elif room.rtype == "W":
            self.canvas.create_oval(tlx+1, tly+1, brx-2, bry-2, fill="SpringGreen3", outline="")
            self.canvas.create_text(tlx+10, tly+10, text="◀", fill="dark green", font=("Helvetica", 12))
        elif room.rtype == "S":
            self.canvas.create_oval(tlx+1, tly+1, brx-2, bry-2, fill="SpringGreen3", outline="")
            self.canvas.create_text(tlx+10, tly+10, text="▼", fill="dark green", font=("Helvetica", 12))
        else:
            self.canvas.create_rectangle(tlx+1, tly+1, brx-2, bry-2, fill="white", outline="")            
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
        print("Start mapping")
        # for level in range(1, 2):
        level = 6
        result = self.breadth_first_search(level)
        print(f"Level {level} ", result)



def main(argv):
    runner = MazeRunner("/Users/wbustraa/Downloads/40 by 20 orthogonal maze.png")
    runner.run()

if __name__ == "__main__":
    main(sys.argv[1:])