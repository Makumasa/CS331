from anytree import AnyNode

def solution(node):
    sol = [node.state]
    cur_node = node

    while cur_node.parent is not None:
        cur_node = node.parent
        sol.insert(0, cur_node.state)

    return sol

def expand(node):
    children = []
    this_side, that_side = ("left", "right") if node.state["left"]["boat"] else ("right", "left")
    this_state = node.state[this_side]
    that_state = node.state[that_side]

    def move_boat(chickens=0, wolves=0):
        new_state = node.state
        new_state[this_side]["boat"] = False
        new_state[that_side]["boat"] = True
        new_state[this_side]["chickens"] -= chickens;
        new_state[that_side]["chickens"] += chickens;
        new_state[this_side]["wolves"] -= wolves;
        new_state[that_side]["wolves"] += wolves;
        return new_state

    if this_state["chickens"] >= 1 and (this_state["chickens"] - 1) >= this_state["wolves"]:
        child_state = move_boat(chickens=1)
        children.append[AnyNode(state=child_state, parent=node)]

        if this_state["chickens"] >= 2 and (this_state["chickens"] - 2) >= this_state["wolves"]:
            child_state = move_boat(chickens=2)
            children.append[AnyNode(state=child_state, parent=node)]
    
    if this_state["wolves"] >= 1 and that_state["chickens"] >= (that_state["wolves"] + 1):
        child_state = move_boat(wolves=1)
        children.append[AnyNode(state=child_state, parent=node)]

    if this_state["wolves"] >= 1 and this_state["chickens"] >= 1:
        child_state = move_boat(chickens=1, wolves=1)
        children.append[AnyNode(state=child_state, parent=node)]

    if this_state["wolves"] >= 2 and that_state["chickens"] >= (that_state["wolves"] + 2):
        child_state = move_boat(wolves=2)
        children.append[AnyNode(state=child_state, parent=node)]

    return children

def bfs(init_state, goal_state, mode):
    if init_state == goal_state:
        return [init_state]
    frontier = [AnyNode(state=init_state)]
    explored = []
    while True:
        if len(frontier) == 0:
            return None
        node = frontier.pop(0)
        explored.append(node.state)

