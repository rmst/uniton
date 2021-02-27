from collections import deque


class QueuedRenderer:
  """
  Uses two queues:
    Unity GPU (render) --render_queue--> Unity CPU --ipc_queue--> Python

  This is not ideal. The ipc queue should be replaced with a push mechanism once that is possible.

  Reduces to non-queued rendering for render_steps = ipc_steps = 1
  """
  def __init__(self, camera, width, height, render_steps=4, ipc_steps=3, fill=True):
    self.camera = camera
    self.render_steps = render_steps
    self.ipc_steps = ipc_steps
    self.ue = camera.ue
    self._render = self.ue.Uniton.RenderTools.RenderAsync
    self._readback_wait = self.ue.Uniton.RenderTools.WaitReadbackRequest
    texture_fmt = self.ue.RenderTextureFormat.ARGB32
    get_texture = self.ue.RenderTexture.GetTemporary
    self.textures = [get_texture(width, height, 0, texture_fmt) for _ in range(render_steps)]
    self.render_queue = deque(maxlen=render_steps)
    self.ipc_queue = deque(maxlen=ipc_steps)
    self.num_req = 0

    if fill:
      for i in range(render_steps+ipc_steps):
        self.render()

  @property
  def delay(self):
    return self.render_steps + self.ipc_steps - 2

  def render(self):
    self.camera.targetTexture = self.textures[self.num_req % self.render_steps]
    readback_request = self._render(self.camera)
    self.render_queue.append(readback_request)
    self.num_req += 1

    if self.num_req >= self.render_steps and self.render_queue:
      self.ipc_queue.append(self._readback_wait(self.render_queue.popleft()).py)

    if self.num_req >= self.render_steps + self.ipc_steps and self.ipc_queue:
      return self.ipc_queue.popleft().wait()
    else:
      return None

  def close(self):
    [self.ue.RenderTexture.ReleaseTemporary(t) for t in self.textures]