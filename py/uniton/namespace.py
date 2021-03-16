from functools import lru_cache
from .csutil import topy


# noinspection PyProtectedMember
class Namespace:
  ue = None

  def __init__(self, ue, ns=""):
    self.ue = ue
    self._ns = ns

  def __getattr__(self, k):

    # this shit below is necessary because somehow @property and @cached_property is interfering with __getattr__
    if k == '_namespaces':
      self._namespaces = self._get_namespaces()
      return self._namespaces
    if k == '_typenames':
      self._typenames = self._get_typenames()
      return self._typenames
    # -----

    if (
      k in ("_ipython_canary_method_should_not_exist_", "_repr_mimebundle_")  # this is needed for the ipython console
      or k.startswith('_')  # probably Python internal
    ):
      raise AttributeError(f'{self} does not have a property called {k}')

    # print("gettr", self._ns, k)

    full_name = self._ns + '.' + k if self._ns else k

    if k in self._namespaces:
      v = Namespace(self.ue, full_name)
    elif k in self._typenames:
      # TODO: make class CsType and cache methods?
      v = self.ue._backend.GetTypeByFullName(full_name)
    elif self._ns == "" and k in self.UnityEngine._namespaces + self.UnityEngine._typenames:
      v = getattr(self.UnityEngine, k)
    else:
      if self._ns == "":
        raise AttributeError(f"'{k}' is not a type or namespace in root nor UnityEngine")
      else:
        raise AttributeError(f"'{k}' is not a type or namespace in {self._ns}")

    if v is not None:  # occurs after exceptions
      vars(self)[k] = v  # next time __getattr__ won't be called again
    return v

  def _get_namespaces(self):
    x = self.ue._backend.GetNamespaces(self._ns)  # C# <System.String[]>
    x = [e.py for e in x]
    x = (e.wait() for e in x)
    x = (e.split('.')[-1] for e in x)
    x = (e for e in x if e.isidentifier())
    return list(set(x))

  def _get_typenames(self):
    x = self.ue._backend.GetTypenamesInNamespace(self._ns)
    x = topy(list(x))
    x = (e.split('.')[-1] for e in x)
    x = (e for e in x if e.isidentifier())
    return list(set(x))

  def __dir__(self):
    r = super().__dir__()
    r += self._namespaces
    r += self._typenames
    if not self._ns:  # root ns
      r += self.UnityEngine._namespaces
      r += self.UnityEngine._typenames
      # r += self.System._typenames
    r = list(set(r))
    return r

  def __repr__(self):
    return f"<uniton.Namespace> '{self._ns}'"
