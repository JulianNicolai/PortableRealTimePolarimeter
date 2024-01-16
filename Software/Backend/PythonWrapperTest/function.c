#include <stdint.h>
#include <Python.h>

PyObject *process_function(int array[], size_t size) {
    npy_int dim = size;
    return PyArray_SimpleNewFromData(1, &dim, (void *) array);
}