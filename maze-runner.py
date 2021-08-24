#!/usr/bin/env python3
from collections import deque as queue
import requests
import sys
import tkinter
from tkinter import ttk


MAZE_LEVEL_BASE_URL = "https://brentts-maze-runner.herokuapp.com//mazerunner/"

m = 100
n = 100

class BrenttMap:
    def check_path(self, level, path):
        url = MAZE_LEVEL_BASE_URL + str(level)
        response = requests.put(url, json=path)
        return response.text


class Node:
    def __init__(self, x: int, y: int, path: tuple):
        super().__init__()
        self.x = x
        self.y = y
        self.path = path

    def neighbor(self, direction):
        if direction == "N":
            return Node(self.x, self.y - 1, self.path + (direction,) )
        elif direction == "E":
            return Node(self.x + 1, self.y, self.path + (direction,) )
        elif direction == "W":
            return Node(self.x - 1, self.y, self.path + (direction,) )
        else:
            return Node(self.x, self.y + 1, self.path + (direction,) )


class MazeRunner:
    def __init__(self, map, scale = 20):
        self.map = map
        self.scale = scale
        self.level = '1'

    def show(self):
        self.root = tkinter.Tk()
        self.root.title('Maze Runner')
        self.canvas = tkinter.Canvas(self.root, bg="white", height=300, width=300)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.btn_frame = ttk.Frame(self.root)

        levels = ('1', '2', '3', '4', '5', '6', '7')
        self.level_chooser = ttk.Combobox(self.btn_frame, width=2, textvariable=self.level, value=levels, state='readonly')
        self.level_chooser.current(0)
        self.level_chooser.pack(side = tkinter.LEFT, padx=10)

        self.button = tkinter.Button(self.btn_frame, text="Start", command=self.start_mapping)
        self.button.pack(side = tkinter.LEFT)

        self.btn_frame.pack()

        self.root.update_idletasks()
        self.root.update()

        self.root.mainloop()

    def draw_node(self, node, node_type):
        tlx = node.x * self.scale
        tly = node.y * self.scale
        brx = tlx + self.scale
        bry = tly + self.scale
        if node.x == 0 and node.y == 0:
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="green")
        elif node_type == "#":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="black")
        elif node_type == "X":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="red")
        elif node_type == "_":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="white")
        elif node_type == "P":
            self.canvas.create_rectangle(tlx, tly, brx, bry, fill="PaleGreen1")
        self.canvas.update_idletasks()
        self.canvas.update()
        

    def breadth_first_search(self, level):

        q = queue()

        start = Node(0, 0, tuple())
        q.append(start)

        visited = [[None for x in range(n)] for x in range(m)]

        exits = []

        shortest_found = False

        while q:
            node = q.popleft()

            visited[node.x][node.y] = "_"
            self.draw_node(node, "_")

            dirs = ["E", "S"]
            if node.y > 0:
                dirs.append("N")
            if node.x > 0:
                dirs.append("W")

            for d in dirs:
                neighbor = node.neighbor(d)

                if visited[neighbor.x][neighbor.y]:
                    continue

                valid = self.map.check_path(level, neighbor.path)

                if valid == "Open Space":
                    q.append(neighbor)
                elif valid == "Wall":
                    visited[neighbor.x][neighbor.y] = "#"
                    self.draw_node(neighbor, "#")
                    continue
                else:
                    visited[neighbor.x][neighbor.y] = "X"
                    self.draw_node(neighbor, "X")
                    print(valid)
                    exits.append(neighbor.path)

                    if not shortest_found:
                        shortest_found = True

                        last = start
                        for step in neighbor.path[:-1]:
                            next = last.neighbor(step)
                            self.draw_node(next, "P")
                            last = next


        return exits

    def start_mapping(self):
        self.canvas.delete("all")
        level = int(self.level_chooser.get())
        result = self.breadth_first_search(level)
        print(f"Level {level} ", result)    

def main(argv):
    runner = MazeRunner(BrenttMap())
    runner.show()

if __name__ == "__main__":
    main(sys.argv[1:])