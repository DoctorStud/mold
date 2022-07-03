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


class Op:
    def __init__(self, left: str, name: str, right: str):
        self.name = name
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left}{self.name}{self.right}"

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


Expr = Union[Sym, Fun, Op]


class Def:
    def __init__(self, head: Expr, body: Expr):
        self.head = head
        self.body = body
        self.name = self.head.name

    def __str__(self):
        return f"{self.head.__str__()} = {self.body.__str__()}"

    def apply_all(self, expr: Expr) -> Expr:
        if bindings := pattern_match(self.head, expr):
            return self.substitute_bindings(bindings, self.body)
        if isinstance(expr, Sym):
            return expr
        if isinstance(expr, Fun):
            new_args = [self.apply_all(arg) for arg in expr.args]
            return Fun(expr.name, *new_args)
        if isinstance(expr, Op):
            return self.substitute_bindings(bindings, expr)

    def substitute_bindings(self, bindings: dict, expr: Expr) -> Expr:
        if isinstance(expr, Sym):
            return bindings.get(expr, expr)
        if isinstance(expr, Fun):
            new_name = ""
            new_name = bindings.get(expr.name, expr.name)
            new_args = [self.substitute_bindings(bindings, arg) for arg in expr.args]
            return Fun(new_name, *new_args)
        if isinstance(expr, Op):
            new_left = bindings.get(expr.left, expr.left)
            new_right = bindings.get(expr.right, expr.right)
            return Op(new_left, expr.name, new_right)


def pattern_match_impl(pattern: Expr, value: Expr, bindings: dict) -> bool:
    if isinstance(pattern, Sym):
        if pattern in bindings:
            return bindings[pattern] == value
        bindings[pattern] = value
        return True
    if isinstance(pattern, Fun) and isinstance(value, Fun):
        if pattern != value or len(pattern.args) != len(value.args):
            return False
        return all(
            pattern_match_impl(pattern.args[i], value.args[i], bindings)
            for i in range(len(pattern.args))
        )
    if isinstance(pattern, Op) and isinstance(value, Op) and pattern.name == value.name:
        pattern_match_impl(pattern.left, value.left, bindings)
        pattern_match_impl(pattern.right, value.right, bindings)
        return True
    return False


def pattern_match(pattern: Expr, value: Expr) -> dict:
    bindings = {}
    if pattern_match_impl(pattern, value, bindings):
        return bindings
    return False


def print_bindings(bindings):
    # print("{")
    for key, val in bindings.items():
        print(f"  {key} => {val}")
    # print("}")


swap = Def(
    Fun("swap", Fun("pair", Sym("a"), Sym("b"))), Fun("pair", Sym("b"), Sym("a"))
)

com = Def(Fun("com", Op(Sym("A"), "+", Sym("B"))), Op(Sym("B"), "+", Sym("A")))

expr = Fun("swap", Fun("pair", Sym("d"), Sym("d")))

expr2 = Fun("com", Op(Sym("C"), "+", Fun("com", Op(Sym("D"), "+", Sym("E")))))

definition = com
expression = expr2


def main():
    print(f"Def: {definition}")
    print(f"Expr: {expression}")
    if pattern_match_result := pattern_match(definition.head, expression):
        print("Bindings:")
        print_bindings(pattern_match_result)
    else:
        print("[ERROR]")
    print(f"Result: {definition.apply_all(expression)}")


if __name__ == "__main__":
    main()
