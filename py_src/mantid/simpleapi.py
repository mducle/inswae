from micromantid.simpleapi import *
from micromantid.simpleapi import _create_algorithm_function as _create_alg_fn
def _create_algorithm_function(name, version, algm_object):
   alg_wrapper = _create_alg_fn(name, version, algm_object)
   globals()[name] = alg_wrapper
   return alg_wrapper