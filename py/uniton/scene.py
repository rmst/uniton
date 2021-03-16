"""
Under construction

To implement this properly we need know about the C# type of each CsObject, see ../../Readme.md

Generally the code in here might be convenient but is slow in principle and poorly written
"""

from .csutil import topy


GETATTR_BLACKLIST = (
  "_ipython_canary_method_should_not_exist_",  # ipython console uses this
  "_repr_mimebundle_",  # ipython console uses this
)


class Scene:
  """
  """
  def __init__(self, scene):
    self._scene = scene
    self._wrapped_cs_object = scene

  def __getattr__(self, item):
    if item.startswith('_') or item in GETATTR_BLACKLIST:
      raise AttributeError()

    gos = self._scene.GetRootGameObjects()
    names = _go_names(gos)
    try:
      idx = names.index(item)
    except ValueError:
      raise AttributeError(f"GameObject with name '{item}' not a child of {self}")

    return GameObject(gos[idx])

  def __dir__(self):
    gos = self._scene.GetRootGameObjects()
    names = _go_names(gos)
    names = [n for n in names if n.isidentifier()]
    return names + super().__dir__()

  def __repr__(self):
    return f"Scene '{self._scene.name.py()}'"


def _go_names(gos):
  names = topy([go.name for go in gos])
  names = [n.replace(' ', '_') for n in names]
  return names


class GameObject:
  _CS_GAMEOBJECT_MEMBERS = [
    'SetActive',
    'isStatic',
    # 'transform',  # manually handled
    # 'ToString',
    'GetInstanceID',
    'activeSelf',
    'GetComponent',
    'scene',
    'tag',
    'GetType',
    'activeInHierarchy',
    'active',
    'Equals',
    'CreatePrimitive',
    'GetHashCode',
    'GetComponentsInChildren',
    'GetComponentInParent',
    'AddComponent',
    'FindGameObjectsWithTag',
    'GetComponents',
    'FindGameObjectWithTag',
    'hideFlags',
    'CompareTag',
    'name',
    'SetActiveRecursively',
    'Find',
    'GetComponentsInParent',
    'SendMessageUpwards',
    'layer',
    'GetComponentInChildren',
    'SendMessage',
    'sceneCullingMask',
    'FindWithTag',
    # 'gameObject',  # what is this?
    'TryGetComponent',
    'BroadcastMessage',
  ]

  _CS_TRANSFORM_MEMBERS = [
    # 'Equals',
    'forward',
    'RotateAroundLocal',
    'GetChild',
    'FindChild',
    'right',
    'GetComponentsInChildren',
    'tag',
    'GetInstanceID',
    'GetEnumerator',
    # 'gameObject',
    'TransformVector',
    'GetComponents',
    'hideFlags',
    # 'GetType',
    'GetComponentInParent',
    'up',
    'SetAsFirstSibling',
    'localToWorldMatrix',
    # 'transform',
    'SendMessageUpwards',
    'DetachChildren',
    'position',
    'hierarchyCapacity',
    'parent',
    'GetComponent',
    'InverseTransformDirection',
    'hasChanged',
    'localScale',
    'RotateAround',
    'SendMessage',
    'LookAt',
    'SetParent',
    'Rotate',
    # 'ToString',
    'eulerAngles',
    'GetSiblingIndex',
    'Translate',
    'TransformDirection',
    'rotation',
    'CompareTag',
    # 'GetHashCode',
    'GetChildCount',
    'InverseTransformPoint',
    'GetComponentsInParent',
    'BroadcastMessage',
    'localEulerAngles',
    'lossyScale',
    'root',
    'hierarchyCount',
    'worldToLocalMatrix',
    'InverseTransformVector',
    'Find',
    'IsChildOf',
    'TransformPoint',
    'TryGetComponent',
    'SetSiblingIndex',
    # 'name',
    'localPosition',
    'SetAsLastSibling',
    'GetComponentInChildren',
    'childCount',
    'localRotation',
    'SetPositionAndRotation',
  ]

  def __init__(self, go):
    self._go = go
    self._wrapped_cs_object = go

    # Transform and GameObject should be the same class: https://forum.unity.com/threads/strange-question-why-are-there-separate-transform-and-gameobject-classes.468451/
    # we combine them here
    self.transform = self._go.transform

  def __getattr__(self, item):
    """
    this is convenient but really slow
    """
    if item.startswith('_') or item in GETATTR_BLACKLIST:
      raise AttributeError()

    if item in GameObject._CS_GAMEOBJECT_MEMBERS:
      return getattr(self._go, item)

    if item in GameObject._CS_TRANSFORM_MEMBERS:
      return getattr(self._go.transform, item)

    cos = self._components()
    co_names = topy([co.GetType().Name for co in cos])
    if item in co_names:
      idx = co_names.index(item)
      co = cos[idx]
      return co

    gos = self._children()
    go_names = _go_names(gos)
    if item in go_names:
      idx = go_names.index(item)
      return GameObject(gos[idx])

    raise AttributeError(f"'{item}' is neither a component, child nor attribute of {self}")

  def _children(self):
    trans = self._go.transform
    n = trans.GetChildCount().py()
    children = [trans.GetChild(i) for i in range(n)]
    return [child.gameObject for child in children]

  def _components(self):
    # TODO: this is a bad hack put this on the C# side
    cos = self._go.GetComponents(self._go.ue.Component)
    isnulls = topy([self._go.ue.System.Object.Equals(co, self._go.ue._null) for co in cos])
    cos = [co for co, isnull in zip(cos, isnulls) if not isnull]
    return cos

  def __dir__(self):
    co_names = topy([co.GetType().Name for co in self._components()])
    go_names = _go_names(self._children())

    names = [n for n in (co_names + go_names) if n.isidentifier()]
    names += GameObject._CS_GAMEOBJECT_MEMBERS
    names += GameObject._CS_TRANSFORM_MEMBERS
    names += super().__dir__()
    return names

  def __repr__(self):
    return f"GameObject '{self._go.name.py()}'"