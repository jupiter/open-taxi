import math
import s2sphere


EARTH_CIRC_METERS = 1000 * 40075.017;


def meters_to_radians(meters):
    return (2 * math.pi) * (meters / EARTH_CIRC_METERS);


def get_cellid_at_level(latitude, longitude, level):
    ll = s2sphere.LatLng.from_degrees(latitude, longitude)
    cell = s2sphere.Cell.from_lat_lng(ll)
    return cell.id().parent(level)

def get_cellids_in_range(latitude, longitude, range_in_meters, min_level, max_level, max_cells, level_mod=1):
    ll = s2sphere.LatLng.from_degrees(latitude, longitude)

    cap = s2sphere.Cap(ll.to_point(), (meters_to_radians(range_in_meters) ** 2) / 2)

    cap_rect_bound = cap.get_rect_bound()

    coverer = s2sphere.RegionCoverer()
    coverer.min_level = min_level
    coverer.max_level = max_level
    coverer.max_cells = max_cells
    coverer.level_mod = level_mod
    cell_ids = coverer.get_covering(cap)
    return cell_ids


def get_hierarchy_as_tokens(cellid, min_level=10, max_level=16, level_mod=2, placeholder='x'):
    tokens = []
    expected_rem = min_level % level_mod
    for x in range(min_level, max_level + 1):
        if not expected_rem == x % level_mod:
            continue
        if cellid.level() < x:
            if placeholder != None:
                tokens.append(placeholder)
        else:
            tokens.append(cellid.parent(x).to_token())
    return tokens
