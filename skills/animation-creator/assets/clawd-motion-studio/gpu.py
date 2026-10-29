"""Enable Cycles Metal GPU rendering. Pass -P gpu.py on every render: the compute
device is a user preference, not part of the .blend."""
import bpy

prefs = bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type = "METAL"
prefs.get_devices()
for d in prefs.devices:
    d.use = d.type == "METAL"
    print("cycles device:", d.name, d.type, "on" if d.use else "off")
for sc in bpy.data.scenes:
    sc.cycles.device = "GPU"
