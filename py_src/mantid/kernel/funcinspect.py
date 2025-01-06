# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
#   NScD Oak Ridge National Laboratory, European Spallation Source,
#   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
# SPDX - License - Identifier: GPL - 3.0 +
"""
Defines functions that can be used to inspect the properties of a
function call. For example

    lhs_info() can be used to get retrieve the names and number of
               arguments that are being assigned to a function
               return
"""

import inspect
import dis

OPERATOR_NAMES = {
    "CALL_FUNCTION", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW", "CALL",
    "UNARY_POSITIVE", "UNARY_NEGATIVE", "UNARY_NOT", "UNARY_CONVERT", "UNARY_INVERT", "GET_ITER",
    "BINARY_POWER", "BINARY_MULTIPLY", "BINARY_DIVIDE", "BINARY_FLOOR_DIVIDE", "BINARY_TRUE_DIVIDE",
    "BINARY_MODULO", "BINARY_ADD", "BINARY_SUBTRACT", "BINARY_SUBSCR", "BINARY_LSHIFT",
    "BINARY_RSHIFT", "BINARY_AND", "BINARY_XOR", "BINARY_OR",
    "INPLACE_POWER", "INPLACE_MULTIPLY", "INPLACE_DIVIDE", "INPLACE_TRUE_DIVIDE", "INPLACE_FLOOR_DIVIDE",
    "INPLACE_MODULO", "INPLACE_ADD", "INPLACE_SUBTRACT", "INPLACE_LSHIFT", "INPLACE_RSHIFT",
    "INPLACE_AND", "INPLACE_XOR", "INPLACE_OR", "COMPARE_OP", "SET_UPDATE", "BUILD_CONST_KEY_MAP",
    "CALL_FUNCTION_EX", "LOAD_METHOD", "CALL_METHOD", "DICT_MERGE", "DICT_UPDATE", "LIST_EXTEND",
}

def process_frame(frame):
    """Returns the number of arguments on the left of assignment along with the names of the variables for the given frame."""
    # Index of the last attempted instruction in byte code
    ins_stack = []
    last_i = frame.f_lasti
    call_function_locs = {}
    start_index = 0
    start_offset = 0
    for index, ins in enumerate(dis.get_instructions(frame.f_code)):
        ins_stack.append(ins)
        if ins.opname in OPERATOR_NAMES:
            call_function_locs[start_offset] = (start_index, index)
            start_index = index
            start_offset = ins.offset
    # Append the index of the last entry to form the last boundary
    call_function_locs[start_offset] = (start_index, len(ins_stack) - 1)
    output_var_names = []
    if last_i not in call_function_locs:
        last_i = max(call_function_locs.keys())
    last_func_offset = call_function_locs[last_i][0]
    # On Windows since migrating to Python 3.10, the last instruction index appears to
    # be one step behind where it should be. We think it's related to the comment here:
    # https://github.com/python/cpython/blob/v3.8.3/Python/ceval.c#L1139
    if ins_stack[last_func_offset].opname == "DICT_MERGE" and ins_stack[last_func_offset + 1].opname in OPERATOR_NAMES:
        last_func_offset += 1
        last_i = ins_stack[last_func_offset + 1].offset
    name, argvalue = (getattr(ins_stack[last_func_offset + 1], k) for k in ['opname', 'argval'])
    if name == "POP_TOP":  # no return values
        pass
    elif name == "STORE_FAST" or name == "STORE_NAME":  # one return value
        output_var_names.append(argvalue)
    elif name == "UNPACK_SEQUENCE":  # Many Return Values, One equal sign
        for index in range(argvalue):
            output_var_names.append(ins_stack[last_func_offset + 2 + index].argval)
    max_returns = len(output_var_names)
    if name == "DUP_TOP":  # Many Return Values, Many equal signs
        count = 0
        max_returns = 0  # Must count the max_returns ourselves in this case
        while count < len(ins_stack[call_function_locs[last_i][0] : call_function_locs[last_i][1]]):
            multi_name, multi_argvalue = (getattr(ins_stack[call_function_locs[last_i][0] + count], k) for k in ['opname', 'argval'])
            if multi_name == "UNPACK_SEQUENCE":  # Many Return Values, One equal sign
                hold = []
                if multi_argvalue > max_returns:
                    max_returns = multi_argvalue
                for index in range(multi_argvalue):
                    hold.append(ins_stack[call_function_locs[last_i][0] + count + 1 + index].argval)
                count += multi_argvalue
                output_var_names.append(hold)
            # Need to now skip the entries we just appended with the for loop.
            if multi_name == "STORE_FAST" or multi_name == "STORE_NAME":  # One Return Value
                if max_returns == 0:
                    max_returns = 1
                output_var_names.append(multi_argvalue)
            count += 1
    return max_returns, tuple(output_var_names)

# -------------------------------------------------------------------------------
def lhs_info(output_type="both", frame=None):
    """Returns the number of arguments on the left of assignment along with the names of the variables."""
    if not frame:
        try:
            # Two frames back so that we get the callers' caller, i.e. this should only
            # be called from within a function
            frame = inspect.currentframe().f_back.f_back
        except AttributeError:
            raise RuntimeError("lhs_info cannot be used on the command line, only within a function")
    try:
        ret_vals = process_frame(frame)
    finally:
        del frame
    if output_type == "nreturns":
        return ret_vals[0]
    elif output_type == "names":
        return ret_vals[1]
    else:
        return ret_vals
