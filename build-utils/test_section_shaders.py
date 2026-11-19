"""Compile all section shader pairs and exercise the actual desktop shaders on Mesa."""
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

import moderngl

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("gouraud", "mm_gouraud", "flat_clip")

with tempfile.TemporaryDirectory() as directory:
    for profile in ("110", "140", "ES"):
        for name in NAMES:
            pair = []
            for source_ext, stage in (("vs", "vert"), ("fs", "frag")):
                source = ROOT / "resources/shaders" / profile / f"{name}.{source_ext}"
                target = Path(directory) / f"shader.{stage}"
                shutil.copyfile(source, target)
                pair.append(str(target))
            subprocess.run(["glslangValidator", "-l", *pair], check=True)

ctx = moderngl.create_standalone_context(backend="egl", require=310)
framebuffer = ctx.simple_framebuffer((64, 64), components=4)
framebuffer.use()
identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
identity3 = struct.pack("9f", 1, 0, 0, 0, 1, 0, 0, 0, 1)
positions = (-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, -1, 0, 1, 1, 0, -1, 1, 0)
buffer = ctx.buffer(struct.pack("18f", *positions))
normals = ctx.buffer(struct.pack("18f", *((0, 0, 1) * 6)))

for name in NAMES:
    shaders = ROOT / "resources/shaders/140"
    program = ctx.program(vertex_shader=(shaders / f"{name}.vs").read_text(),
                          fragment_shader=(shaders / f"{name}.fs").read_text())
    for uniform in ("view_model_matrix", "projection_matrix", "volume_world_matrix"):
        program[uniform].write(identity)
    if "view_normal_matrix" in program:
        program["view_normal_matrix"].write(identity3)
    program["z_range"].value = (-10, 10)
    program["uniform_color"].value = (1, 1, 1, 1)
    attributes = [(buffer, "3f", "v_position")]
    if "v_normal" in program:
        attributes.append((normals, "3f", "v_normal"))
    vao = ctx.vertex_array(program, attributes)
    # Test translated cut planes and each combination of directions.
    for first_sign in (-1, 1):
        for second_sign in (-1, 1):
            for offset in (-0.25, 0, 0.25):
                first = (first_sign, 0, 0, offset)
                second = (0, second_sign, 0, -offset)
                program["clipping_plane"].value = first
                program["compound_clipping_plane"].value = second
                for compound in (False, True):
                    program["use_compound_clipping"].value = compound
                    framebuffer.clear(0, 0, 0, 0)
                    vao.render()
                    image = framebuffer.read(components=4, alignment=1)
                    for py in (8, 24, 40, 56):
                        for px in (8, 24, 40, 56):
                            x, y = (px + 0.5) / 32 - 1, (py + 0.5) / 32 - 1
                            removed = first_sign * x + offset < 0
                            if compound:
                                removed = removed and second_sign * y - offset < 0
                            alpha = image[4 * (py * 64 + px) + 3]
                            assert (alpha == 0) == removed, (name, first, second, compound, x, y, alpha)
    # Existing Z clipping must still take precedence in compound mode.
    program["z_range"].value = (1, 2)
    program["use_compound_clipping"].value = True
    framebuffer.clear(0, 0, 0, 0)
    vao.render()
    assert not any(framebuffer.read(components=4, alignment=1)), name
    print(f"{name}: compound, reverse, offset, single-plane and Z clipping passed")

print("All 9 shader pairs linked; 1,152 GPU pixel assertions passed.")
