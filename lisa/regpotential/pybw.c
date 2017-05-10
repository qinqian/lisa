#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include "pybw.h"
#define RP_DOC "Summarize data from bigwig file as regulatory potential returns numpy array of scores. bwfile_name, chrom_list, start_list, end_list, strand_list, weights, option (mean,max,min)"

static PyObject *RPError;

static PyObject *
getrp(PyObject *self, PyObject *args) // self is the module object
{
  PyObject *bigwigfileObj;  /* bigwig file name strings */
  PyObject *bedfile;   /* bed file name strings */
  PyObject *outfile; 
  PyObject *decay;  
  PyObject *left;  
  PyObject *right; 
  char *bigWigFile; 
  char *bed;
  char *out;
  double d;
  int l;
  int r;
#if PY_MAJOR_VERSION >= 3
#define PyInt_Type PyLong_Type
#define PyString_Type PyBytes_Type 
#define PyInt_AsLong PyLong_AsLong
#define PyString_AsString PyBytes_AsString
#endif
  //if (! PyArg_ParseTuple( args, "O!O!O!O!O!O!", &PyString_Type, &bigwigfileObj, &PyString_Type, &bedfile, &PyString_Type, &outfile, &PyFloat_Type, &decay, &PyInt_Type, &left, &PyInt_Type, &right)) {
  if (! PyArg_ParseTuple( args, "sssO!O!O!", &bigWigFile, &bed, &out, &PyFloat_Type, &decay, &PyInt_Type, &left, &PyInt_Type, &right)) {
    printf("%s %s %s %f %d %d \n", bigWigFile, bed, out, d, l, r);
    PyErr_SetString(RPError, "something bad happened!!!");
    return NULL;
  }
  //bigWigFile = PyString_AsString(bigwigfileObj);
  //bed = PyString_AsString(bedfile);
  //out = PyString_AsString(outfile);
  d = PyFloat_AsDouble(decay);
  l = PyInt_AsLong(left);
  r = PyInt_AsLong(right);
  printf("%s %s %s %f %d %d \n", bigWigFile, bed, out, d, l, r);

  bigWigAverageOverBed(bigWigFile, bed, out, d, l, r);

  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef myMethods[] = {
    { "getrp", getrp, METH_VARARGS, RP_DOC },
    { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "_bw",
        "epigenomics data RP module", 
        -1,
        myMethods,
        NULL,
        NULL,
        NULL,
        NULL
};

#define INITERROR return NULL
//PyObject *
PyMODINIT_FUNC
PyInit__bw(void)
#else
#define INITERROR return
//PyMODINIT_FUNC init_bw(void)
void init_bw(void)
#endif
{       
#if PY_MAJOR_VERSION >= 3
    PyObject *m = PyModule_Create(&moduledef);
#else
    PyObject *m = Py_InitModule("_bw", myMethods);
#endif
    if (m == NULL)
        INITERROR;

    RPError = PyErr_NewException("_bw.Error", NULL, NULL);
    Py_INCREF(RPError);
    PyModule_AddObject(m, "rperror", RPError);
    /* import_array(); */
#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}
