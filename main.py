import pygame
import sys
import heapq
import tkinter as tk
import tkinter.messagebox
import tkinter.simpledialog
import re
import os

#Global variables
DISPLAY_WIDTH = 500
DISPLAY_HEIGHT = 500
COLUMNS = 50
ROWS = 50
WHITE_COLOUR = [255, 255, 255]
BLUE_COLOUR = [0, 0, 255]
RED_COLOUR = [255, 0, 0]
GREEN_COLOUR = [0, 255, 0]
BLACK_COLOUR = [0, 0, 0]
GREY_COLOUR = [88, 88, 88]
YELLOW_COLOUR = [255,255,0]
POSS_MOVES = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1))
SHOW_CALC = False
BLOCKED_NODES = []

# Create the pygame window here so we can reference it throughout
screen = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
pygame.display.set_caption("Pathfinder")
pygame.init()

#Classes
class Node():
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position

        # Setup some default values
        self.blocked = False
        self.width = DISPLAY_WIDTH / COLUMNS
        self.height = DISPLAY_HEIGHT / ROWS

        # Setup A* vars (formula is: f = h + g)
        self.f = 0
        self.g = 0
        self.h = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __gt__(self, other):
        return self.f > other.f

#Functions
def wait():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def drawNode(colour,c,r,thickness=0):
        pygame.draw.rect(screen,colour,(c * DISPLAY_WIDTH / COLUMNS, r * DISPLAY_HEIGHT / ROWS, DISPLAY_WIDTH / COLUMNS, DISPLAY_WIDTH / ROWS),thickness)
        pygame.display.update()

def calcPathway(node):
    calc_path = []
    path_node = node

    while path_node is not None:
        calc_path.append(path_node.position)
        path_node = path_node.parent
    return calc_path[::-1]

def promptNode(type):
    input_win = tk.Tk()
    input_win.withdraw()
    while True:
        node = tkinter.simpledialog.askstring(title="Value Entry",prompt=f"Please enter the {type} (x,y):")
        format_check = re.search("[(][0-9]?[0-9],[0-9]?[0-9][)]", node)

        if format_check:
            return node
        else:
            tkinter.messagebox.showwarning("Invalid Value",f"Incorrect value for the {type} node, please try again.")

def addObs(mpos,start,end):
    x = mpos[0]
    y = mpos[1]
    x = x // (DISPLAY_WIDTH // COLUMNS)
    y = y // (DISPLAY_HEIGHT // ROWS)

    if start != (x,y) and end != (x,y):
        BLOCKED_NODES.append((x,y))
        drawNode(WHITE_COLOUR,x,y)

def astarPathFinder(node_map,start_node_pos,end_node_pos):
    # Setup the two node lists
    open_list = []
    closed_list = []
    heapq.heapify(open_list)

    # Create the start and end nodes
    start_node = Node(None,start_node_pos)
    end_node = Node(None,end_node_pos)

    heapq.heappush(open_list,start_node)

    # While we have nodes to check
    while len(open_list) > 0:
        #Re draw nodes
        for node in open_list:
            if node != start_node and node.position not in BLOCKED_NODES:
                drawNode(GREEN_COLOUR,node.position[0],node.position[1])
        for node in closed_list:
            if node != start_node and node.position not in BLOCKED_NODES:
                drawNode(RED_COLOUR,node.position[0],node.position[1])

        # Get the current node
        curr_node = heapq.heappop(open_list)
        closed_list.append(curr_node)
        if curr_node.position in BLOCKED_NODES:
            curr_node.blocked = True

        # Check if we've reached the end goal
        if curr_node == end_node:
            return calcPathway(curr_node)

        neighbours = []

        for movement in POSS_MOVES:
            # Get the new position
            new_node_pos = (curr_node.position[0] + movement[0],curr_node.position[1] + movement[1])

            # Check if it actually exists on the grid
            if new_node_pos[0] > (len(node_map) - 1) or new_node_pos[0] < 0 or new_node_pos[1] > (
                    len(node_map[len(node_map) - 1]) - 1) or new_node_pos[1] < 0:
                continue

            # Check if node is blocked
            if curr_node.blocked == True:
                continue

            new_node = Node(curr_node,new_node_pos)
            neighbours.append(new_node)

        # Perform calculations on all eligible neighbours
        for n in neighbours:
            if n in closed_list:
                continue

            n.g = curr_node.g + 1
            n.h = ((n.position[0] - end_node.position[0]) ** 2) + ((n.position[1] - end_node.position[1]) ** 2)
            n.f = n.g + n.h

            if n in open_list:
                continue

            heapq.heappush(open_list,n)

    tkinter.messagebox.showwarning("Path Calc","Unable to calculate a viable path")
    return None


#Runtime
def main():
    # Setup the node grid
    grid = []

    for row in range(ROWS):
        grid.append([])
        for col in range(COLUMNS):
            grid[row].append(0)

    # Create the grid
    for row in range(ROWS):
        for col in range(COLUMNS):
            drawNode(GREY_COLOUR,col,row,1)

    start = promptNode("start")
    start = eval(start)
    end = promptNode("end")
    end = eval(end)
    drawNode(YELLOW_COLOUR,start[0],start[1])
    drawNode(YELLOW_COLOUR, end[0],end[1])

    # Build the obstacles
    configuring = True
    while configuring:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mpos = pygame.mouse.get_pos()
                addObs(mpos,start,end)
            elif pygame.mouse.get_pressed()[0]:
                mpos = pygame.mouse.get_pos()
                addObs(mpos,start,end)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                configuring = False

    path = astarPathFinder(grid,start,end)
    # print(path)
    # wait()

    result = tk.messagebox.askokcancel("Pathfinder Finished","Path calculation complete, do you want to start again?")
    if result:
        screen.fill(BLACK_COLOUR)
        pygame.display.update()
        os.execl(sys.executable,sys.executable,* sys.argv)
    else:
        tk.messagebox.showinfo("Pathfinder Finished","Close to exit")
        wait()

main()