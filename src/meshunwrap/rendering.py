from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from meshunwrap.geometry import MeshData
from meshunwrap.uv import UVResult


def _style_3d_axes(ax: plt.Axes) -> None:
    ax.set_axis_off()
    ax.view_init(elev=22, azim=-62)


def render_mesh_figure(mesh: MeshData, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(8, 6), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    triangles = mesh.points[mesh.faces]
    collection = Poly3DCollection(triangles, linewidths=0.15, alpha=0.95)
    collection.set_facecolor("#8fb7cf")
    collection.set_edgecolor("#31576a")
    ax.add_collection3d(collection)
    ax.auto_scale_xyz(mesh.points[:, 0], mesh.points[:, 1], mesh.points[:, 2])
    _style_3d_axes(ax)
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight")
    plt.close(fig)
    return target


def render_normal_figure(mesh: MeshData, path: str | Path, sample_index: int | None = None) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    idx = len(mesh.points) // 3 if sample_index is None else sample_index
    point = mesh.points[idx]
    normal = mesh.normals[idx]
    scale = 0.35 * np.linalg.norm(np.ptp(mesh.points, axis=0))

    fig = plt.figure(figsize=(8, 6), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    triangles = mesh.points[mesh.faces]
    collection = Poly3DCollection(triangles, linewidths=0.1, alpha=0.3)
    collection.set_facecolor("#bcd5e3")
    collection.set_edgecolor("#52788d")
    ax.add_collection3d(collection)
    ax.scatter(point[0], point[1], point[2], color="#1d4f6b", s=20)
    ax.quiver(
        point[0],
        point[1],
        point[2],
        normal[0],
        normal[1],
        normal[2],
        length=scale * 0.18,
        color="#c0392b",
        linewidth=2.2,
    )
    ax.auto_scale_xyz(mesh.points[:, 0], mesh.points[:, 1], mesh.points[:, 2])
    _style_3d_axes(ax)
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight")
    plt.close(fig)
    return target


def render_uv_figure(result: UVResult, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 5), dpi=160)
    ax.scatter(result.uv[:, 0], result.uv[:, 1], s=12, c=result.theta, cmap="viridis", linewidths=0.0)
    ax.set_xlabel("phi (wrapped)")
    ax.set_ylabel("theta")
    ax.set_title("UV mapping")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(target, bbox_inches="tight")
    plt.close(fig)
    return target
