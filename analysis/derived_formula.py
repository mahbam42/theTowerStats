"""Safe evaluation for simple derived-metric formulas.

Derived chart configs reference base metric keys in a small expression language.
This module evaluates those expressions safely (no attribute access, no calls,
no comprehensions) and returns None when inputs are missing.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping


def evaluate_formula(formula: str, variables: Mapping[str, float | None]) -> float | None:
    """Evaluate a derived-metric formula using provided variables.

    Args:
        formula: Expression referencing metric keys as identifiers (e.g. "a / b").
        variables: Mapping from identifier name to numeric value (or None).

    Returns:
        The computed float value, or None when inputs are missing/invalid.
    """

    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError:
        return None

    return _eval_node(tree.body, variables)


def _eval_node(node: ast.AST, variables: Mapping[str, float | None]) -> float | None:
    """Recursively evaluate an AST node with strict safety rules."""

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        return None

    if isinstance(node, ast.Name):
        value = variables.get(node.id)
        return float(value) if value is not None else None

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _eval_node(node.operand, variables)
        if operand is None:
            return None
        return operand if isinstance(node.op, ast.UAdd) else -operand

    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        left = _eval_node(node.left, variables)
        right = _eval_node(node.right, variables)
        if left is None or right is None:
            return None
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                return None
            return left / right

    return None

