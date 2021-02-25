from functools import cached_property


class Namespace:
  _con = None

  def __init__(self, con, ns=()):
    self._con = con
    self._ns = ns

  def __getattr__(self, k):
    if (
      k in ("_ipython_canary_method_should_not_exist_", "_repr_mimebundle_") # this is needed for the ipython console
      or k.startswith('_')  # probably Python internal
    ):
      raise AttributeError()

    # print("gettr", self._ns, k)

    if k in self._namespaces:
      v = Namespace(self._con, ns=(*self._ns, k))
    else:
      v = self._con.u.GetTypeInNamespace(k, '.'.join(self._ns))

    if v is not None:  # occurs after exceptions
      vars(self)[k] = v  # next time __getattr__ won't be called again
    return v

  @cached_property
  def _namespaces(self):
    x = self._con.u.GetNamespaces('.'.join(self._ns))  # C# <System.String[]>
    x = [e.to_py() for e in x]
    x = (e.wait() for e in x)
    x = (e.split('.')[-1] for e in x)
    x = (e for e in x if e.isidentifier())
    return list(x)

  @property
  def _typenames(self):
    x = self._con.u.GetTypenamesInNamespace('.'.join(self._ns))
    x = [e.to_py() for e in x]
    x = (e.wait() for e in x)
    x = (e for e in x if e.isidentifier())
    return list(x)

  def __dir__(self):
    r = super().__dir__()
    r += self._typenames
    r += self._namespaces
    r = list(set(r))
    return r