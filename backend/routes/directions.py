from flask import Blueprint, request, jsonify
from models import Location, Path
from sqlalchemy import and_
import heapq
from collections import defaultdict, deque

directions_bp = Blueprint("directions", __name__)

# ----------------------------------------------------------
#  Graph Helpers
# ----------------------------------------------------------

def build_graph():
    """Load all paths from DB and return adjacency list."""
    graph = defaultdict(list)
    paths = Path.query.all()

    for p in paths:
        graph[p.start_id].append((p.end_id, p.distance))
        graph[p.end_id].append((p.start_id, p.distance))   # undirected
    return graph

def dijkstra(graph, start, end):
    """Return shortest path using Dijkstra."""
    pq = [(0, start, [])]
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        new_path = path + [node]

        if node == end:
            return cost, new_path

        for neighbor, w in graph[node]:
            if neighbor not in visited:
                heapq.heappush(pq, (cost + w, neighbor, new_path))

    return float("inf"), []


def yen_k_shortest_paths(graph, start, end, k=3):
    """Return top-k shortest paths between start and end."""
    # First shortest path
    cost, path = dijkstra(graph, start, end)
    if not path:
        return []

    routes = [(cost, path)]
    candidates = []

    for i in range(1, k):
        prev_cost, prev_path = routes[-1]

        for j in range(len(prev_path) - 1):
            spur_node = prev_path[j]
            root_path = prev_path[: j + 1]

            removed_edges = []

            # Remove edges that conflict with the root path
            for cost_r, path_r in routes:
                if len(path_r) > j and root_path == path_r[: j + 1]:
                    u = path_r[j]
                    v = path_r[j + 1]

                    # Remove edge u->v
                    for idx, (nbr, w) in enumerate(graph[u]):
                        if nbr == v:
                            removed_edges.append((u, (nbr, w), idx))
                            graph[u].pop(idx)
                            break

            # Spur path
            spur_cost, spur_path = dijkstra(graph, spur_node, end)

            if spur_path:
                total_cost = spur_cost + sum(
                    graph[root_path[n]][root_path[n + 1]][0]
                    for n in range(len(root_path) - 1)
                )
                full_path = root_path[:-1] + spur_path

                candidates.append((total_cost, full_path))

            # Restore edges
            for u, edge, idx in removed_edges:
                graph[u].insert(idx, edge)

        if not candidates:
            break

        # Pick shortest candidate
        candidates.sort(key=lambda x: x[0])
        routes.append(candidates.pop(0))

    return routes[:k]


def path_to_steps(node_list):
    """Convert list of location IDs into readable steps."""
    locs = {loc.id: loc for loc in Location.query.filter(Location.id.in_(node_list))}
    steps = []

    for i in range(len(node_list)):
        loc = locs[node_list[i]]
        if i == 0:
            steps.append(f"Start at {loc.name}")
        else:
            steps.append(f"Walk to {loc.name}")

    return steps


# ----------------------------------------------------------
#  ROUTE ENDPOINT — returns top 3 best routes
# ----------------------------------------------------------

@directions_bp.route("/", methods=["GET"])
def compute_route():

    start_id = request.args.get("start", type=int)
    end_id = request.args.get("end", type=int)

    if not start_id or not end_id:
        return jsonify({"error": "start and end are required"}), 400

    if start_id == end_id:
        return jsonify({"error": "start and end cannot be the same"}), 400

    graph = build_graph()
    results = yen_k_shortest_paths(graph, start_id, end_id, k=3)

    output = []
    for cost, path in results:
        steps = path_to_steps(path)
        output.append({
            "distance": cost,
            "path": path,
            "steps": steps
        })

    return jsonify({
        "routes": output,
        "count": len(output)
    })
