from typing import Union
import pprint


class Sym:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Fun:
    def __init__(self, name: str, *argv: list[Union[Sym, "Fun"]]):
        self.name = name
        self.args = argv

    def __str__(self):
        args_len = len(self.args)
        args = ", ".join(f"{arg}" for arg in self.args)
        return f"{self.name}({args})"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


class Op:
    def __init__(self, left: str, name: str, right: str):
        self.name = name
        self.left = left
        self.right = right

    def __str__(self):
        if isinstance(self.left, Op) and isinstance(self.right, Op):
            return f"({self.left}){self.name}({self.right})"
        elif isinstance(self.left, Op):
            return f"({self.left}){self.name}{self.right}"
        elif isinstance(self.right, Op):
            return f"{self.left}{self.name}({self.right})"
        return f"{self.left}{self.name}{self.right}"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


Expr = Union[Sym, Fun, Op]


class Def:
    def __init__(self, name: str, head: Expr, body: Expr):
        self.name = name
        self.head = head
        self.body = body

    def __str__(self):
        return f"{self.name} := {self.head.__str__()} = {self.body.__str__()}"

    def apply(self, expr: Expr, match_lvl: int) -> Expr:
        if bindings := pattern_match(self.head, expr, match_lvl):
            return self.substitute(bindings, expr, match_lvl)

    def substitute(self, bindings, expr, match_lvl: int) -> Expr:
        if match_lvl != 0:
            if isinstance(expr, Op):
                expr.left = self.substitute(bindings, expr.left, match_lvl - 1)
                expr.right = self.substitute(bindings, expr.right, match_lvl - 1)
                return expr
            if isinstance(expr, Fun):
                new_args = [
                    self.substitute(bindings, arg, match_lvl - 1) for arg in expr.args
                ]
                expr.args = new_args
                return expr
        else:
            if isinstance(expr, Sym) and any(bindings[i] == expr for i in bindings):
                return bindings.get(self.body, self.body)
            if (
                isinstance(expr, Op)
                and any(bindings[i] == expr.left for i in bindings)
                and any(bindings[i] == expr.right for i in bindings)
            ):
                new_left = bindings.get(self.body.left, self.body.left)
                new_right = bindings.get(self.body.right, self.body.right)
                return Op(new_left, expr.name, new_right)
            if isinstance(expr, Fun) and set(expr.args).issubset(bindings.values()):
                new_name = bindings.get(self.body.name, self.body.name)
                new_args = [bindings.get(arg, arg) for arg in self.body.args]
                return Fun(new_name, *new_args)
        return expr


def pattern_match(pattern: Expr, value: Expr, match_lvl: int) -> dict:
    bindings = {}
    if pattern_match_impl(pattern, value, bindings, match_lvl):
        return bindings
    return None


def pattern_match_impl(
    pattern: Expr, value: Expr, bindings: dict, match_lvl: int
) -> bool:
    if match_lvl != 0:
        if isinstance(value, Op):
            pattern_match_impl(pattern, value.left, bindings, match_lvl - 1)
            pattern_match_impl(pattern, value.right, bindings, match_lvl - 1)
            return True
        if isinstance(value, Fun):
            return any(
                pattern_match_impl(pattern, value.args[i], bindings, match_lvl - 1)
                for i in range(len(value.args))
            )
        return False
    else:
        if isinstance(pattern, Sym):
            if pattern in bindings:
                return bindings[pattern] == value
            bindings[pattern] = value
            return True
        if isinstance(pattern, Fun) and isinstance(value, Fun):
            if pattern != value or len(pattern.args) != len(value.args):
                return False
            return all(
                pattern_match_impl(pattern.args[i], value.args[i], bindings, match_lvl)
                for i in range(len(pattern.args))
            )
        if (
            isinstance(pattern, Op)
            and isinstance(value, Op)
            and pattern.name == value.name
        ):
            pattern_match_impl(pattern.left, value.left, bindings, match_lvl)
            pattern_match_impl(pattern.right, value.right, bindings, match_lvl)
            return True
    return False
