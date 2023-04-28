
class Error():
    def __init__(self, name, message):
        self.name = name
        self.message = message
        self.throw()

    def __str__(self):
        return f"[ERROR] {self.name}: {self.message}\n"

    def throw(self):
        return self


class PetternMatchError(Error):
    def __init__(self):
        super().__init__("PatternMatchError", "Unable to match pattern to expression")


class Sym:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Var:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{{{self.name}}}"

    def __hash__(self):
        return 2*hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Fun:
    def __init__(self, name, *args):
        self.name = name
        self.args = list(args)

    def __repr__(self):
        args = ", ".join(f"{arg}" for arg in self.args)
        return f"{self.name}({args})"

    def __hash__(self):
        return 3*hash(self.name) + sum(hash(arg)*(i+1) for i, arg in enumerate(self.args))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Op:
    def __init__(self, left, name, right):
        self.name = name
        self.left = left
        self.right = right

    def __repr__(self):
        if isinstance(self.left, Op) and isinstance(self.right, Op):
            return f"({self.left}) {self.name} ({self.right})"
        elif isinstance(self.left, Op):
            return f"({self.left}) {self.name} {self.right}"
        elif isinstance(self.right, Op):
            return f"{self.left} {self.name} ({self.right})"
        return f"{self.left} {self.name} {self.right}"

    def __hash__(self):
        return hash(self.name) + 2*hash(self.left) + 3*hash(self.right)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Def:
    def __init__(self, name, head, body):
        self.name = name
        self.head = head
        self.body = body

    def __repr__(self):
        return f"{self.name} := {self.head.__str__()} = {self.body.__str__()}"

    def apply(self, expr, strat=None, debug=False):
        if bindings := pattern_match(self.head, expr):
            if debug:
                print_bindings(bindings)
            return self.substitute(self.body, bindings, strat=strat, debug=debug)
        else:
            if isinstance(expr, Sym):
                return expr
            elif isinstance(expr, Op):
                left = self.apply(expr.left, strat=strat, debug=debug)
                right = self.apply(expr.right, strat=strat, debug=debug)
                return Op(left, expr.name, right)
            elif isinstance(expr, Fun):
                new_args = [self.apply(arg, strat=strat, debug=debug)
                            for arg in expr.args]
                return Fun(expr.name, *new_args)

    def substitute(self, expr, bindings, strat=None, debug=False):
        if isinstance(expr, Sym):
            return bindings.get(expr, expr)
        if isinstance(expr, Op):
            if bindings.get(expr):
                return bindings[expr]
            else:
                if strat == "all":
                    new_left = self.apply(bindings.get(
                        self.body.left, self.body.left), strat=strat, debug=debug)
                    new_right = self.apply(bindings.get(
                        self.body.right, self.body.right), strat=strat, debug=debug)
                    return Op(new_left, self.body.name, new_right)
                else:
                    new_left = bindings.get(self.body.left, self.body.left)
                    new_right = bindings.get(self.body.right, self.body.right)
                    return Op(new_left, self.body.name, new_right)

        if isinstance(expr, Fun):
            if bindings.get(expr):
                return bindings[expr]
            else:
                if strat == "all":
                    new_args = [self.apply(bindings.get(arg), strat=strat, debug=debug)
                                for arg in expr.args]
                    return Fun(self.body.name, *new_args)
                else:
                    new_args = [bindings.get(arg)
                                for arg in expr.args]
                    return Fun(self.body.name, *new_args)


def pattern_match(pattern, expr):
    bindings = {}
    if pattern_match_impl(pattern, expr, bindings):
        return bindings


def pattern_match_impl(pattern, expr, bindings):
    if isinstance(pattern, Var):
        if pattern in bindings:
            return bindings[pattern] == expr
        bindings[pattern] = expr
        return True
    if isinstance(pattern, Sym) and expr == pattern:
        bindings[pattern] = expr
        return True
    if isinstance(pattern, Fun) and isinstance(expr, Fun):
        if pattern.name == expr.name and len(pattern.args) != len(expr.args):
            return False
        return all(
            pattern_match_impl(
                pattern.args[i], expr.args[i], bindings)
            for i, _ in enumerate(pattern.args))

    if isinstance(pattern, Op) and isinstance(expr, Op) and pattern.name == expr.name:
        pattern_match_impl(pattern.left, expr.left, bindings)
        pattern_match_impl(pattern.right, expr.right, bindings)
        return True


def list_nodes(expr):
    queue = []
    nodes = []
    if nodes is None:
        nodes = []
    queue.append(expr)
    while queue:
        node = queue.pop(0)
        nodes.append(node)
        if isinstance(node, Op):
            queue.append(node.left)
            queue.append(node.right)
        elif isinstance(node, Fun):
            for arg in node.args:
                queue.append(arg)
    return nodes


def print_bindings(bindings: dict):
    print("{")
    for key, val in bindings.items():
        print(f"  {key} => {val}")
    print("}")
