import logging
from copy import deepcopy
from sys import argv
from heapq import heappush, heappop

"""A simple node class that holds its state, its key, its parent and its depth."""
class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.key = str(self.state)
        self.depth = 0
        ancestor = self.parent
        while ancestor is not None:
            self.depth += 1
            ancestor = ancestor.parent

"""Constructs a state object from data in a file."""
def state_from_file(file_name):

    with open(file_name, "r") as file:
        line = file.readline()
        left_values = list(map(int, line.split(",")))
        line = file.readline()
        right_values = list(map(int, line.split(",")))

    state = {}
    state["left"], state["right"] = {}, {}
    state["left"]["chickens"]  = left_values[0]
    state["left"]["wolves"]    = left_values[1]
    state["left"]["boat"]      = False if left_values[2] == 0 else True
    state["right"]["chickens"] = right_values[0]
    state["right"]["wolves"]   = right_values[1]
    state["right"]["boat"]     = False if right_values[2] == 0 else True

    return state

"""Prints the results of the search in the expected format to stdout and a file."""
def print_solution(states, expanded, out_file):
    level = logging.INFO
    format = "%(message)s"
    handlers = [logging.FileHandler(out_file, mode="w"), 
                logging.StreamHandler()]
    logging.basicConfig(level=level, format=format, handlers=handlers)
    
    logging.info("nodes expanded: {0}".format(expanded))

    if states is None:
        print("no solution found")

    else:
        logging.info("nodes in solution: {0}\n".format(len(states)))

        for state in states:
            zero = state["left"]["chickens"]
            one  = state["left"]["wolves"]
            two  = 0 if state["left"]["boat"] else 1
            logging.info("{0},{1},{2}".format(zero, one, two))
            zero = state["right"]["chickens"]
            one  = state["right"]["wolves"]
            two  = 0 if state["right"]["boat"] else 1
            logging.info("{0},{1},{2}\n".format(zero, one, two))

"""
The heuristic function for the A* search. It assigns an expected cost of 2 per animal on the right
bank because in almost every case it takes a minimum of two moves to get one animal off the right
bank (two animals to the left bank at most, one animal has to come back). The only time this isn't
true is during the final trip in which up to two animals can be moved over in one turn. This
exception is offset in two ways. First, in the case where the boat is at the right bank, a cost
reduction of 3 is applied, which outweighs the slight deviation from the average animals per turn
for the last turn. In the case where the boat is at the left bank, the cost reduction need not be
applied because that is when the expected cost is already overly optimistic. This is because neither
the animal that still has to be sent back (+2 points) nor the turn it takes to go back to the right
bank (+1 point) is factored into the heuristic cost in the left bank case. Thus, the function is
an optimistic approximation for all states and is therefore admissible.
"""
def hueristic(node):
    cost = node.depth
    cost += node.state["right"]["chickens"] * 2
    cost += node.state["right"]["wolves"] * 2
    if node.state["right"]["boat"]:
        cost -= 3
    return cost

"""Builds a list of solution states in order from a goal node."""
def solution(node):
    sol = [node.state]
    cur_node = node

    while cur_node.parent is not None:
        cur_node = cur_node.parent
        sol.insert(0, cur_node.state)

    return sol

"""Generates a list of children produced through legal actions for a given node."""
def expand(node):
    children = []
    this_side, that_side = ("left", "right") if node.state["left"]["boat"] else ("right", "left")
    this_state = node.state[this_side]
    that_state = node.state[that_side]

    """Helper function that applies a movement of an arbitrary number of animals to a state."""
    def move_boat(chickens=0, wolves=0):
        new_state = deepcopy(node.state)
        new_state[this_side]["boat"] = False
        new_state[that_side]["boat"] = True
        new_state[this_side]["chickens"] -= chickens;
        new_state[that_side]["chickens"] += chickens;
        new_state[this_side]["wolves"] -= wolves;
        new_state[that_side]["wolves"] += wolves;
        return new_state

    """Determines whether or not a potential child state is legal by the puzzle's rules."""
    def is_valid(state):
        if state["left"]["chickens"] < 0 or state["left"]["wolves"] < 0:
            return False
        if state["right"]["chickens"] < 0 or state["right"]["wolves"] < 0:
            return False
        if state["left"]["chickens"] > 0 and state["left"]["chickens"] < state["left"]["wolves"]:
            return False
        if state["right"]["chickens"] > 0 and state["right"]["chickens"] < state["right"]["wolves"]:
            return False
        return True

    """The list of successor states in the expected order."""
    states = [move_boat(chickens=1),
              move_boat(chickens=2),
              move_boat(wolves=1),
              move_boat(chickens=1,wolves=1),
              move_boat(wolves=2)]

    for state in states:
        if is_valid(state):
            children.append(Node(state, parent=node))

    return children

"""A general graph_search algorithm capable of working in BFS, DFS, IDDFS, and A* modes."""
def graph_search(init_state, goal_state, mode):
    expanded = 0        # Counter for number of nodes expanded.
    depth = 0           # Current depth (for iddfs).
    max_depth = 500     # Upper limit on depth before giving up.
    q_count = 0         # Unique ID for priority queue elements to break ties in favor of FIFO.

    if init_state == goal_state:
        return [init_state]
    init_node = Node(init_state)
    explored = {}

    # In the A* case, the frontier is a priority queue, otherwise it's just a list.
    frontier = []
    if mode == "astar":
        heappush(frontier, (hueristic(init_node), q_count, init_node))
        q_count += 1
    else:
        frontier.append(init_node)

    # Runs until depth limit is reached, the search fails, or the search succeeds.
    while True:
        if len(frontier) == 0:
            # In the IDDFS case, we simply restart the search with an increased depth. 
            if mode == "iddfs":
                if depth >= max_depth:
                    return None
                frontier.append(init_node)
                explored = {}
                depth += 1
            # In all other cases, the search fails.
            else:
                return None, expanded

        # For A*, we expand the node with the lowest cost first.
        if mode == "astar":
            _, _, node = heappop(frontier)
        # For BFS, we expand nodes in FIFO order.
        elif mode == "bfs":
            node = frontier.pop(0)
        # For DFS and IDDFS, we expand nodes in LIFO order.
        else:
            node = frontier.pop()

        # Our explored set is implemented with a map between IDs unique to states and their depth.
        explored[node.key] = node.depth

        # For IDDFS, we do not expand nodes at or above our current depth limit.
        if mode == "iddfs" and node.depth >= depth:
            continue

        # Now that we know we will expand this node, increment the counter.
        expanded += 1

        # For each successor node...
        for child in expand(node):
            # Skip nodes that are already in the frontier. 
            # A caveat is made to address the fact frontier is a list of triples in the A* case. 
            if mode == "astar":
                if any(x for x in frontier if x[2].state == child.state):
                    continue
            else:
                if any(x for x in frontier if x.state == child.state):
                    continue

            # Skip nodes that are already in the explored set.
            if child.key in explored:
                # For IDDFS, we first verify that the successor isn't at a shallower depth.
                if mode != "iddfs" or child.depth >= explored[child.key]:
                    continue
                # If it is, we don't skip but instead update the depth associated with it.
                else:
                    explored[child.key] = child.depth

            # Return as soon as we find a goal node.
            if child.state == goal_state:
                return solution(child), expanded

            # Add each valid successor to the frontier.
            if mode == "astar":
                heappush(frontier, (hueristic(child), q_count, child))
                q_count += 1
            else:
                frontier.append(child)

"""Our main method simply gets the command line arguments and performs the desired search."""
if __name__ == "__main__":
    init_state = state_from_file(argv[1])
    goal_state = state_from_file(argv[2])
    solution, expanded = graph_search(init_state, goal_state, argv[3])
    print_solution(solution, expanded, argv[4])
