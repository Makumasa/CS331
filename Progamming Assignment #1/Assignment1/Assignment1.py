import logging
from copy import deepcopy
from anytree import AnyNode
from sys import argv

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

def print_solution(states, expanded, out_file):
    level = logging.INFO
    format = "%(message)s"
    handlers = [logging.FileHandler(out_file, mode="w"), logging.StreamHandler()]
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

def solution(node):
    sol = [node.state]
    cur_node = node

    while cur_node.parent is not None:
        cur_node = cur_node.parent
        sol.insert(0, cur_node.state)

    return sol

def expand(node):
    children = []
    this_side, that_side = ("left", "right") if node.state["left"]["boat"] else ("right", "left")
    this_state = node.state[this_side]
    that_state = node.state[that_side]

    def move_boat(chickens=0, wolves=0):
        new_state = deepcopy(node.state)
        new_state[this_side]["boat"] = False
        new_state[that_side]["boat"] = True
        new_state[this_side]["chickens"] -= chickens;
        new_state[that_side]["chickens"] += chickens;
        new_state[this_side]["wolves"] -= wolves;
        new_state[that_side]["wolves"] += wolves;
        return new_state

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

    states = [move_boat(chickens=1),
              move_boat(chickens=2),
              move_boat(wolves=1),
              move_boat(chickens=1,wolves=1),
              move_boat(wolves=2)]

    for state in states:
        if is_valid(state):
            children.append(AnyNode(parent=node, state=state, key=str(state)))

    return children

def graph_search(init_state, goal_state, mode):
    expanded = 0
    depth = 0
    max_depth = 50000
    if init_state == goal_state:
        return [init_state]
    frontier = [AnyNode(state=init_state, key=str(init_state))]
    explored = {}

    while True:
        if len(frontier) == 0:
            if mode == "iddfs":
                if depth >= max_depth:
                    return None
                frontier = [AnyNode(state=init_state, key=str(init_state))]
                explored = {}
                depth += 1
            else:
                return None, expanded

        node = frontier.pop(0) if mode == "bfs" else frontier.pop()
        explored[node.key] = node.depth
        if mode == "iddfs" and node.depth >= depth:
            continue
        expanded += 1

        children = expand(node)
        for child in children:
            if any(x for x in frontier if x.state == child.state):
                continue
            if child.key in explored:
                if mode != "iddfs" or child.depth >= explored[child.key]:
                    continue
                else:
                    explored[child.key] = child.depth
            if child.state == goal_state:
                return solution(child), expanded
            frontier.append(child)

def bfs(init_state, goal_state):
    return graph_search(init_state, goal_state, "bfs")

def dfs(init_state, goal_state):
    return graph_search(init_state, goal_state, "dfs")

def iddfs_tree(init_state, goal_state):
    expanded = 0

    def recursive_dls(node, goal_state, depth):
        nonlocal expanded
        if node.state == goal_state:
            return solution(node)
        elif depth == 0:
            return "cutoff"
        else:
            cutoff = False
            expanded += 1
            children = expand(node)
            for child in children:
                result = recursive_dls(child, goal_state, depth - 1)
                if result == "cutoff":
                    cutoff = True
                elif result is not None:
                    return result
            return "cutoff" if cutoff else None

    result = "cutoff"
    depth = 0
    init_node = AnyNode(state=init_state)

    while result == "cutoff":
        if depth > max_depth:
            return None
        result = recursive_dls(init_node, goal_state, depth)
        depth += 1

    return result, expanded

def iddfs(init_state, goal_state):
    return graph_search(init_state, goal_state, "iddfs")

if __name__ == "__main__":
    init_state = state_from_file(argv[1])
    goal_state = state_from_file(argv[2])
    solution, expanded = globals()[argv[3]](init_state, goal_state)
    print_solution(solution, expanded, argv[4])
