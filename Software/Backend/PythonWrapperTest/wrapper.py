from numpy.ctypeslib import ndpointer
import ctypes


clib = ctypes.CDLL("./function.dll", winmode=1)
clib.process_function.restype = ndpointer(dtype=ctypes.c_uint16, shape=(20,))

res = clib.process_function(5, 6)

print(res)