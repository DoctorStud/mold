
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
        self.args = args

    def __repr__(self):
        args = ", ".join(f"{arg}" for arg in self.args)
        return f"{self.name}({args})"

    def __hash__(self):
        return 3*hash(self.name)

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
        return 4*hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Def:
    def __init__(self, name, head, body):
        self.name = name
        self.head = head
        self.body = body

    def __repr__(self):
        return f"{self.name} := {self.head.__str__()} = {self.body.__str__()}"

    def apply(self, expr):
        if bindings := pattern_match(self.head, expr):
            if isinstance(expr, Sym) and any(bindings[i] == expr for i in bindings):
                return self.substitute(bindings)
            if (
                isinstance(expr, Op)
                and any(bindings[i] == expr.left for i in bindings)
                and any(bindings[i] == expr.right for i in bindings)
            ):
                return self.substitute(bindings)
            if isinstance(expr, Fun) and set(expr.args).issubset(bindings.values()):
                return self.substitute(bindings)

    def substitute(self, bindings):
        if isinstance(self.body, Sym):
            return bindings.get(self.body, self.body)
        if isinstance(self.body, Fun):
            new_name = bindings.get(self.body.name, self.body.name)
            new_args = [bindings.get(arg, arg) for arg in self.body.args]
            return Fun(new_name, *new_args)
        if isinstance(self.body, Op):
            new_left = bindings.get(self.body.left, self.body.left)
            new_right = bindings.get(self.body.right, self.body.right)
            return Op(new_left, self.body.name, new_right)


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
        if pattern != expr or len(pattern.args) != len(expr.args):
            return False
        return all(
            pattern_match_impl(
                pattern.args[i], expr.args[i], bindings)
            for i, _ in enumerate(pattern.args))

    if isinstance(pattern, Op) and isinstance(expr, Op) and pattern.name == expr.name:
        pattern_match_impl(pattern.left, expr.left, bindings)
        pattern_match_impl(pattern.right, expr.right, bindings)
        return True


def list_nodes(expr, nodes=None):
    if nodes is None:
        nodes = []
    if isinstance(expr, Sym) or isinstance(expr, Var):
        nodes.append(expr)
        return nodes
    if isinstance(expr, Fun):
        nodes.append(expr)
        for arg in expr.args:
            list_nodes(arg, nodes)
        return nodes
    if isinstance(expr, Op):
        nodes.append(expr)
        list_nodes(expr.right, nodes)
        list_nodes(expr.left, nodes)
        return nodes
    return nodes
