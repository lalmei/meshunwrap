"""Pure NumPy UV parameterization helpers for tubular meshes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

POINT_ARRAY_NDIM = 2
POINT_DIMENSIONS = 3
FACE_VERTICES = 3


@dataclass
class SeamResult:
    """A traced seam path plus the vertices that lie west of each seam step."""

    path: np.ndarray
    west_of_seam: list[np.ndarray]


@dataclass
class UVResult:
    """UV parameterization outputs and seam bookkeeping for a mesh."""

    uv: np.ndarray
    phi_unwrapped: np.ndarray
    theta: np.ndarray
    north: int
    south: int
    seam_path: np.ndarray
    west_of_seam: list[np.ndarray]


def _as_points(points: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=float)
    if array.ndim != POINT_ARRAY_NDIM or array.shape[1] != POINT_DIMENSIONS:
        raise ValueError("points must be an (n, 3) array")
    return array


def _as_faces(faces: Sequence[Sequence[int]] | np.ndarray) -> np.ndarray:
    array = np.asarray(faces, dtype=int)
    if array.ndim != POINT_ARRAY_NDIM or array.shape[1] != FACE_VERTICES:
        raise ValueError("faces must be an (m, 3) integer array")
    return array


def _normalize_rows(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    out = vectors.copy()
    nonzero = norms[:, 0] > 0.0
    out[nonzero] /= norms[nonzero]
    return out


def _normalize_adjacency(adjacency: Sequence[Iterable[int]], n_vertices: int) -> list[np.ndarray]:
    normalized: list[np.ndarray] = []
    for idx, neighbors in enumerate(adjacency):
        unique = np.array(sorted({int(n) for n in neighbors if int(n) != idx}), dtype=int)
        if np.any(unique < 0) or np.any(unique >= n_vertices):
            raise ValueError("adjacency contains out-of-range vertex indices")
        normalized.append(unique)
    if len(normalized) != n_vertices:
        raise ValueError("adjacency length must match number of points")
    return normalized


def build_adjacency_from_faces(faces: Sequence[Sequence[int]] | np.ndarray, n_vertices: int) -> list[np.ndarray]:
    """Build a vertex adjacency list from a triangle-face array."""
    face_array = _as_faces(faces)
    neighbors: list[set[int]] = [set() for _ in range(n_vertices)]
    for a, b, c in face_array:
        for u, v in ((a, b), (b, c), (c, a)):
            if u < 0 or v < 0 or u >= n_vertices or v >= n_vertices:
                raise ValueError("faces contains out-of-range vertex indices")
            neighbors[u].add(v)
            neighbors[v].add(u)
    return [np.array(sorted(group), dtype=int) for group in neighbors]


def estimate_vertex_normals(
    points: Sequence[Sequence[float]] | np.ndarray,
    faces: Sequence[Sequence[int]] | np.ndarray,
) -> np.ndarray:
    """Estimate area-weighted per-vertex normals from triangle faces."""
    pts = _as_points(points)
    face_array = _as_faces(faces)
    normals = np.zeros_like(pts)
    for face in face_array:
        a, b, c = pts[face]
        area_normal = np.cross(b - a, c - a)
        normals[face] += area_normal

    norms = np.linalg.norm(normals, axis=1)
    missing = norms == 0.0
    if np.any(missing):
        centroid = pts.mean(axis=0)
        fallback = pts[missing] - centroid
        fallback_norms = np.linalg.norm(fallback, axis=1, keepdims=True)
        usable = fallback_norms[:, 0] > 0.0
        fallback[usable] /= fallback_norms[usable]
        fallback[~usable] = np.array([0.0, 0.0, 1.0])
        normals[missing] = fallback

    return _normalize_rows(normals)


def _fallback_normals(points: np.ndarray) -> np.ndarray:
    centroid = points.mean(axis=0)
    normals = points - centroid
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    nonzero = norms[:, 0] > 0.0
    normals[nonzero] /= norms[nonzero]
    normals[~nonzero] = np.array([0.0, 0.0, 1.0])
    return normals


def _interior_index(n_vertices: int, north: int, south: int) -> tuple[np.ndarray, dict[int, int]]:
    mask = np.ones(n_vertices, dtype=bool)
    mask[[north, south]] = False
    interior = np.flatnonzero(mask)
    return interior, {int(vertex): idx for idx, vertex in enumerate(interior)}


def solve_latitudes(
    points: Sequence[Sequence[float]] | np.ndarray,
    adjacency: Sequence[Iterable[int]],
    north: int,
    south: int,
) -> np.ndarray:
    """Solve the harmonic latitude field with fixed north and south poles."""
    pts = _as_points(points)
    adj = _normalize_adjacency(adjacency, len(pts))
    n_vertices = len(pts)
    theta = np.zeros(n_vertices, dtype=float)
    theta[south] = np.pi

    interior, index = _interior_index(n_vertices, north, south)
    if len(interior) == 0:
        return theta

    amat = np.zeros((len(interior), len(interior)), dtype=float)
    bvec = np.zeros(len(interior), dtype=float)

    for vertex in interior:
        row = index[vertex]
        neighbors = adj[vertex]
        amat[row, row] = float(len(neighbors))
        for neighbor in neighbors:
            if neighbor == north:
                continue
            if neighbor == south:
                bvec[row] += np.pi
                continue
            amat[row, index[neighbor]] -= 1.0

    theta[interior] = np.linalg.solve(amat, bvec)
    return theta


def _orientation_sign(points: np.ndarray, normals: np.ndarray, here: int, reference: int, candidate: int) -> float:
    return float(
        np.dot(
            points[candidate] - points[here],
            np.cross(normals[here], points[reference] - points[here]),
        ),
    )


def _classify_west_neighbors(
    points: np.ndarray,
    adjacency: list[np.ndarray],
    normals: np.ndarray,
    previous: int,
    here: int,
    nextpos: int,
) -> np.ndarray:
    turn_sign = _orientation_sign(points, normals, here, previous, nextpos)
    west: list[int] = []
    for candidate in adjacency[here]:
        if candidate in (previous, here, nextpos):
            continue
        sign_prev = _orientation_sign(points, normals, here, previous, candidate)
        sign_next = _orientation_sign(points, normals, here, nextpos, candidate)
        keep = sign_prev < 0.0 or sign_next >= 0.0 if turn_sign > 0.0 else sign_prev < 0.0 and sign_next >= 0.0
        if keep:
            west.append(int(candidate))
    return np.array(west, dtype=int)


def trace_seam(
    points: Sequence[Sequence[float]] | np.ndarray,
    adjacency: Sequence[Iterable[int]],
    normals: Sequence[Sequence[float]] | np.ndarray,
    theta: Sequence[float] | np.ndarray,
    north: int,
    south: int,
) -> SeamResult:
    """Trace a north-to-south seam through the mesh connectivity graph."""
    pts = _as_points(points)
    adj = _normalize_adjacency(adjacency, len(pts))
    nrm = _as_points(normals)
    theta_array = np.asarray(theta, dtype=float)

    if len(adj[north]) == 0:
        raise ValueError("north pole has no adjacent vertices")

    previous = north
    here = int(adj[north][np.argmax(theta_array[adj[north]])])
    path = [north, here]
    west_of_seam: list[np.ndarray] = []
    visited = {north, here}

    for _ in range(len(pts) + 1):
        if here == south:
            break

        neighbors = [int(v) for v in adj[here] if v != previous]
        if not neighbors:
            raise ValueError("failed to trace seam: reached a dead end")

        higher = [v for v in neighbors if theta_array[v] >= theta_array[here] - 1e-12]
        candidates = higher if higher else neighbors
        nextpos = max(
            candidates,
            key=lambda v: (theta_array[v], -np.linalg.norm(pts[v] - pts[south])),
        )

        if nextpos in visited and nextpos != south:
            unvisited = [v for v in candidates if v not in visited]
            if not unvisited:
                raise ValueError("failed to trace seam: loop detected")
            nextpos = max(unvisited, key=lambda v: theta_array[v])

        west = _classify_west_neighbors(pts, adj, nrm, previous, here, nextpos)
        west_of_seam.append(west)
        previous = here
        here = nextpos
        path.append(here)
        visited.add(here)
    else:
        raise ValueError("failed to trace seam from north pole to south pole")

    if path[-1] != south:
        raise ValueError("failed to trace seam from north pole to south pole")

    return SeamResult(path=np.asarray(path, dtype=int), west_of_seam=west_of_seam)


def solve_longitudes(
    points: Sequence[Sequence[float]] | np.ndarray,
    adjacency: Sequence[Iterable[int]],
    theta: Sequence[float] | np.ndarray,
    seam: SeamResult,
    north: int,
    south: int,
) -> np.ndarray:
    """Solve the harmonic longitude field with seam jump constraints."""
    pts = _as_points(points)
    adj = _normalize_adjacency(adjacency, len(pts))
    _ = np.asarray(theta, dtype=float)
    n_vertices = len(pts)
    phi = np.zeros(n_vertices, dtype=float)

    interior, index = _interior_index(n_vertices, north, south)
    if len(interior) == 0:
        return phi

    amat = np.zeros((len(interior), len(interior)), dtype=float)
    bvec = np.zeros(len(interior), dtype=float)

    for vertex in interior:
        row = index[vertex]
        neighbors = adj[vertex]
        amat[row, row] = float(len(neighbors))
        for neighbor in neighbors:
            if neighbor in (north, south):
                continue
            amat[row, index[neighbor]] -= 1.0

    for here, west_neighbors in zip(seam.path[1:-1], seam.west_of_seam):
        if here not in index:
            continue
        here_row = index[int(here)]
        for neighbor in west_neighbors:
            neighbor_index = index.get(int(neighbor))
            if neighbor_index is None:
                continue
            bvec[neighbor_index] += 2.0 * np.pi
            bvec[here_row] -= 2.0 * np.pi

    phi[interior] = np.linalg.solve(amat, bvec)
    phi[north] = 0.0
    phi[south] = 0.0
    return phi


def parameterize_tube(
    points: Sequence[Sequence[float]] | np.ndarray,
    faces: Sequence[Sequence[int]] | np.ndarray | None = None,
    adjacency: Sequence[Iterable[int]] | None = None,
    normals: Sequence[Sequence[float]] | np.ndarray | None = None,
    pole_axis: int = 2,
) -> UVResult:
    """Map a tubular mesh onto UV space using harmonic latitudes and longitudes."""
    pts = _as_points(points)
    if pole_axis not in (0, 1, 2):
        raise ValueError("pole_axis must be 0, 1, or 2")

    face_array = None if faces is None else _as_faces(faces)
    if adjacency is None:
        if face_array is None:
            raise ValueError(
                "surface reconstruction from a raw point cloud is out of scope for this pure-NumPy port; "
                "provide faces or adjacency",
            )
        adj = build_adjacency_from_faces(face_array, len(pts))
    else:
        adj = _normalize_adjacency(adjacency, len(pts))

    if normals is not None:
        normal_array = _as_points(normals)
    elif face_array is not None:
        normal_array = estimate_vertex_normals(pts, face_array)
    else:
        normal_array = _fallback_normals(pts)

    south = int(np.argmin(pts[:, pole_axis]))
    north = int(np.argmax(pts[:, pole_axis]))

    theta = solve_latitudes(pts, adj, north=north, south=south)
    seam = trace_seam(pts, adj, normal_array, theta, north=north, south=south)
    phi_unwrapped = solve_longitudes(pts, adj, theta, seam, north=north, south=south)
    phi_wrapped = (phi_unwrapped + np.pi) % (2.0 * np.pi) - np.pi
    uv = np.column_stack((phi_wrapped, theta))

    return UVResult(
        uv=uv,
        phi_unwrapped=phi_unwrapped,
        theta=theta,
        north=north,
        south=south,
        seam_path=seam.path,
        west_of_seam=seam.west_of_seam,
    )
