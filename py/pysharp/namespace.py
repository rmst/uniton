from functools import cached_property


# noinspection PyProtectedMember
class Namespace:
  cs = None

  def __init__(self, cs, ns=""):
    self.cs = cs
    self._ns = ns

  def __getattr__(self, k):
    if (
      k in ("_ipython_canary_method_should_not_exist_", "_repr_mimebundle_")  # this is needed for the ipython console
      or k.startswith('_')  # probably Python internal
    ):
      raise AttributeError()

    # print("gettr", self._ns, k)

    if k in self._namespaces:
      ns = self._ns + '.' + k if self._ns else k
      v = Namespace(self.cs, ns)
    elif k in self._typenames:
      # TODO: make class CsType and cache methods?
      v = self.cs._backend.GetTypeInNamespace(k, self._ns)
    else:
      raise AttributeError(f"'{k}' is not a type or namespace in {self._ns}")

    if v is not None:  # occurs after exceptions
      vars(self)[k] = v  # next time __getattr__ won't be called again
    return v

  @cached_property
  def _namespaces(self):
    x = self.cs._backend.GetNamespaces(self._ns)  # C# <System.String[]>
    x = [e.py for e in x]
    x = (e.wait() for e in x)
    x = (e.split('.')[-1] for e in x)
    x = (e for e in x if e.isidentifier())
    return list(x)

  @cached_property
  def _typenames(self):
    x = self.cs._backend.GetTypenamesInNamespace(self._ns)
    x = [e.py for e in x]
    x = (e.wait() for e in x)
    x = (e for e in x if e.isidentifier())
    return list(x)

  def __dir__(self):
    r = super().__dir__()
    r += self._typenames
    r += self._namespaces
    r = list(set(r))
    return r