import csv
import math
import sys
from collections import deque


class Airport:

  def __init__(
      self, airport_id: int, code: str, name: str, lat: float, lon: float
  ):
    self.id = airport_id
    self.code = code
    self.name = name
    self.lat = lat
    self.lon = lon

    rad_lat = math.radians(lat)
    rad_lon = math.radians(lon)
    self.x = math.cos(rad_lat) * math.cos(rad_lon)
    self.y = math.cos(rad_lat) * math.sin(rad_lon)
    self.z = math.sin(rad_lat)


class KDNode:

  def __init__(self, airport: Airport, axis: int):
    self.airport = airport
    self.axis = axis
    self.left = None
    self.right = None


def build_kdtree(airports: list[Airport], depth: int = 0) -> KDNode | None:
  if not airports:
    return None

  axis = depth % 3
  if axis == 0:
    airports.sort(key=lambda a: a.x)
  elif axis == 1:
    airports.sort(key=lambda a: a.y)
  else:
    airports.sort(key=lambda a: a.z)

  median_idx = len(airports) // 2
  node = KDNode(airports[median_idx], axis)
  node.left = build_kdtree(airports[:median_idx], depth + 1)
  node.right = build_kdtree(airports[median_idx + 1 :], depth + 1)
  return node


def k_nearest_neighbors(
    node: KDNode | None,
    tx: float,
    ty: float,
    tz: float,
    k: int = 10,
    heap: list = None,
) -> list[tuple[float, Airport]]:
  if heap is None:
    heap = []

  if node is None:
    return heap

  dx = node.airport.x - tx
  dy = node.airport.y - ty
  dz = node.airport.z - tz
  dist = dx * dx + dy * dy + dz * dz

  heap.append((dist, node.airport))
  heap.sort(key=lambda x: x[0])
  if len(heap) > k:
    heap.pop()

  diff = (
      (tx - node.airport.x)
      if node.axis == 0
      else ((ty - node.airport.y) if node.axis == 1 else (tz - node.airport.z))
  )

  first = node.left if diff < 0 else node.right
  second = node.right if diff < 0 else node.left

  heap = k_nearest_neighbors(first, tx, ty, tz, k, heap)

  max_dist = heap[-1][0] if len(heap) == k else float('inf')
  if diff * diff < max_dist:
    heap = k_nearest_neighbors(second, tx, ty, tz, k, heap)

  return heap


class FlightEngine:

  def __init__(self):
    self.airports: dict[str, Airport] = {}
    self.code_alias: dict[str, str] = {}  # Maps both IATA & ICAO to primary code
    self.adj_list: dict[str, set[str]] = {}
    self.kdtree_root: KDNode | None = None

  def load_airports(self, filepath: str) -> None:
    airport_list: list[Airport] = []

    with open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
      reader = csv.reader(f)
      for row in reader:
        if len(row) < 8:
          continue

        iata = row[4].strip()
        icao = row[5].strip()

        # Determine primary identifier
        primary_code = (
            iata if (iata and iata != '\\N') else (icao if icao != '\\N' else None)
        )
        if not primary_code:
          continue

        try:
          lat = float(row[6])
          lon = float(row[7])
          ap = Airport(int(row[0]), primary_code, row[1], lat, lon)

          self.airports[primary_code] = ap
          airport_list.append(ap)

          if iata and iata != '\\N':
            self.code_alias[iata.upper()] = primary_code
          if icao and icao != '\\N':
            self.code_alias[icao.upper()] = primary_code

        except ValueError:
          continue

    self.kdtree_root = build_kdtree(airport_list)

  def load_routes(self, filepath: str) -> None:
    with open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
      reader = csv.reader(f)
      for row in reader:
        if len(row) < 5:
          continue

        src_raw = row[2].strip().upper()
        dst_raw = row[4].strip().upper()

        src = self.code_alias.get(src_raw)
        dst = self.code_alias.get(dst_raw)

        if src and dst:
          if src not in self.adj_list:
            self.adj_list[src] = set()
          self.adj_list[src].add(dst)

  def get_ranked_antipodes(
      self, origin_code: str, count: int = 15
  ) -> list[Airport]:
    origin = self.airports[origin_code]
    anti_lat = -origin.lat
    anti_lon = ((origin.lon + 180.0 + 180.0) % 360.0) - 180.0

    rad_lat = math.radians(anti_lat)
    rad_lon = math.radians(anti_lon)
    tx = math.cos(rad_lat) * math.cos(rad_lon)
    ty = math.sin(rad_lon) * math.cos(rad_lat)
    tz = math.sin(rad_lat)

    neighbors = k_nearest_neighbors(
        self.kdtree_root, tx, ty, tz, k=count, heap=[]
    )
    return [ap for _, ap in neighbors]

  def find_shortest_route(self, start: str, target: str) -> list[str]:
    queue = deque([start])
    parent = {start: None}

    while queue:
      current = queue.popleft()

      if current == target:
        break

      for neighbor in self.adj_list.get(current, []):
        if neighbor not in parent:
          parent[neighbor] = current
          queue.append(neighbor)

    if target not in parent:
      return []

    path = []
    curr = target
    while curr is not None:
      path.append(curr)
      curr = parent[curr]

    path.reverse()
    return path


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('Usage: python main.py <AIRPORT_CODE>')
    sys.exit(1)

  user_input = sys.argv[1].strip().upper()

  engine = FlightEngine()
  print('Loading datasets...')
  engine.load_airports('airports.dat')
  engine.load_routes('routes.dat')

  if user_input not in engine.code_alias:
    print(f"Error: Airport code '{user_input}' not found in database.")
    sys.exit(1)

  origin_code = engine.code_alias[user_input]
  print(f'Origin: {origin_code} ({engine.airports[origin_code].name})')

  candidate_antipodes = engine.get_ranked_antipodes(origin_code, count=20)

  path = []
  selected_target = None

  for candidate in candidate_antipodes:
    res_path = engine.find_shortest_route(origin_code, candidate.code)
    if res_path:
      path = res_path
      selected_target = candidate
      break

  if not path:
    print('No connected flight path found to any nearby antipodal airport.')
  else:
    print(
        f'Closest Reachable Antipode Airport: {selected_target.code} ({selected_target.name})'
    )
    print(f'\nShortest Route ({len(path) - 1} legs):')
    for i, code in enumerate(path):
      print(f'  Leg {i}: {code} - {engine.airports[code].name}')