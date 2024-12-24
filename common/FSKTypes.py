import ctypes

class COMP(ctypes.Structure):
    _fields_ = [("real", ctypes.c_float),
                ("imag", ctypes.c_float)                 
                ]