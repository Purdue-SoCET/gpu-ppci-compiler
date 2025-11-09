from .nodes import types, declarations

def builtin_fty(ret_id, param_ids):
    """Build a FunctionType from types.BasicType ids"""
    # Build types.BasicType instances from string ids like "float", "int"
    ret = types.BasicType(ret_id)
    args = [declarations.ParameterDeclaration(
            None,
            types.BasicType(pid),
            None,
            None
            ) for pid in param_ids]
    return types.FunctionType(args, ret)

BUILTIN_FUNCS = {
    "cos":   builtin_fty(types.BasicType.FLOAT, [types.BasicType.FLOAT]),
    "sin":   builtin_fty(types.BasicType.FLOAT, [types.BasicType.FLOAT]),
    "isqrt": builtin_fty(types.BasicType.FLOAT, [types.BasicType.FLOAT]),
    "itof":  builtin_fty(types.BasicType.FLOAT, [types.BasicType.INT]),
    "ftoi":  builtin_fty(types.BasicType.INT,   [types.BasicType.FLOAT]),
}

def get_builtin_func(name: str):
    """Return a FunctionType or None"""
    return BUILTIN_FUNCS.get(name)
