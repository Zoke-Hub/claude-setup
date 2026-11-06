# Ball joints for paper puppets, fitted to the drawing (shared by the rig scripts).
# The rule that keeps a cut-out limb from coming apart or showing steps when it bends:
#  - the cut between two pieces runs straight through the pivot, square to the limb (at a bent joint: square to the
#    bisector of the two segments);
#  - the pivot sits at the middle of the limb's cross-section along that cut;
#  - the ball (carried by both pieces) has a radius of half that cross-section, so the cut's corners lie on it, but
#    never more than the distance from the pivot to the drawing's nearest edge: at its own pose the puppet is exactly
#    the drawing, and no joint ever bulges out of it.
import numpy as np


def unit(v):
    v = np.asarray(v, float); return v / np.hypot(*v)


def fit_joint(mask, pivot, parent, child=None, reach=400, cap=True):
    """mask: the drawn limb (both segments) as a bool image; pivot: a first guess; parent / child: points along the two
    segments (child=None -> the cut is square to the parent segment alone). Returns (centre, radius, axis): the cut line
    is the line through centre square to axis; pixels with (X - centre) . axis < 0 belong to the parent piece."""
    d1 = unit(np.subtract(pivot, parent))
    d = unit(d1 + unit(np.subtract(child, pivot))) if child is not None else d1
    n = np.array([-d[1], d[0]])
    s = np.arange(-reach, reach + 1)
    pts = np.round(np.asarray(pivot, float)[None, :] + s[:, None] * n[None, :]).astype(int)
    H, W = mask.shape
    ok = (pts[:, 0] >= 0) & (pts[:, 0] < W) & (pts[:, 1] >= 0) & (pts[:, 1] < H)
    v = np.zeros(len(s), bool); v[ok] = mask[pts[ok, 1], pts[ok, 0]]
    mid = reach
    if not v[mid]:                               # start from the nearest limb pixel on the cut line
        on = np.nonzero(v)[0]
        if len(on) == 0: raise ValueError("no limb on the cut line at %s" % (pivot,))
        mid = on[np.argmin(np.abs(on - reach))]
    lo = mid
    while lo > 0 and v[lo - 1]: lo -= 1
    hi = mid
    while hi < len(s) - 1 and v[hi + 1]: hi += 1
    centre = np.asarray(pivot, float) + ((s[lo] + s[hi]) / 2) * n
    c = tuple(int(v) for v in np.round(centre))
    # the ball never reaches past the drawing: at most the distance from the pivot to the limb's nearest edge (a cut
    # that is not quite square to the limb is longer than the limb is wide, and half of it would bulge out)
    r = float((s[hi] - s[lo]) / 2.0)
    if cap: r = min(r, inscribed(mask, c))
    return c, r, (float(d[0]), float(d[1]))


def inscribed(mask, c, box=600):
    """distance from point c to the nearest pixel outside the mask (the radius of the largest circle there that stays
    inside the drawing)"""
    import cv2
    H, W = mask.shape; x, y = c
    x0, y0, x1, y1 = max(x - box, 0), max(y - box, 0), min(x + box, W), min(y + box, H)
    dt = cv2.distanceTransform(np.pad(mask[y0:y1, x0:x1], 1).astype(np.uint8), cv2.DIST_L2, 5)
    return float(dt[y - y0 + 1, x - x0 + 1])


def side_of(xx, yy, centre, axis):
    """signed distance along the limb axis from the cut line (negative = parent side)"""
    return (xx - centre[0]) * axis[0] + (yy - centre[1]) * axis[1]


# A bent joint (an elbow drawn at 90 degrees, a flexed knee) needs more than one cut: a cut along the bisector runs
# diagonally from the inner crease to the outer corner, so half its length is far wider than the limb and the ball
# sticks out as a knob. Instead:
#  - the child segment's centre line and half-width are measured from two cross-sections square to it, away from
#    the bend; the pivot slides back along that line until a ball of that radius just fits in the drawn joint, so
#    the ball meets the outer corner and both edges of the child tangentially (a round elbow with no step);
#  - the parent keeps the drawing on its own side of a cut square to itself through the pivot; everything else, the
#    point of the elbow included, is the child and turns with it (the elbow's point is the end of the forearm bone, so a
#    real elbow keeps its point when it bends; it never becomes a round blob); a hidden flap of the parent fills the
#    inner crease under the child.
# Almost straight joints (under min_angle) keep the single bisector cut of fit_joint.
def sections(mask, a, b, ts, reach=400):
    out = []
    for t in ts:
        p = np.add(a, t * np.subtract(b, a))
        c, r, _ = fit_joint(mask, tuple(p), tuple(p - np.subtract(b, a)), None, reach, cap=False)    # square to a -> b
        out.append((np.array(c, float), r))
    return out


def fit_bend(mask, parent, guess, child, min_angle=20.0, solid=None, ts=(0.45, 0.8)):
    """parent: the parent segment's own pivot (a shoulder, a hip) or a point on its centre line; child: a point on the
    child segment away from the joint (a wrist, an ankle); guess: the joint, roughly. The child's centre line and
    half-width are measured from the drawing; the pivot is moved back along that line until the ball of that radius
    just fits inside the drawn joint (solid: the mask to fit in, default the limb), so the ball meets the outer corner
    and both edges of the child. Returns dict(c, r, ax_p, ax_c, bent, angle)."""
    import cv2
    (c1, _), (c2, _) = sections(mask, guess, child, ts)          # clear of the crease
    dc = unit(c2 - c1)
    c1, rc, _ = fit_joint(mask, tuple(c1), tuple(c1 - dc), None); c1 = np.array(c1, float)   # square to the true axis
    dt = cv2.distanceTransform((mask if solid is None else solid).astype(np.uint8), cv2.DIST_L2, 5)
    H, W = mask.shape; piv = c1.copy(); fit = min(rc, float(dt[int(c1[1]), int(c1[0])])) - 3
    for step in range(1, 2000):
        q = c1 - dc * step; x, y = int(round(q[0])), int(round(q[1]))
        if not (0 <= x < W and 0 <= y < H) or dt[y, x] < fit: break
        piv = q
    dp = unit(piv - np.asarray(parent, float))
    angle = float(np.degrees(np.arccos(np.clip(dp @ dc, -1, 1))))
    if angle < min_angle:
        c, r, ax = fit_joint(mask, guess, parent, child)
        return dict(c=c, r=r, ax_p=ax, ax_c=ax, bent=False, angle=angle)
    c = tuple(int(v) for v in np.round(piv))
    return dict(c=c, r=min(float(rc), inscribed(mask, c)), ax_p=(float(dp[0]), float(dp[1])),
                ax_c=(float(dc[0]), float(dc[1])), bent=True, angle=angle)


def split_bend(xx, yy, mask, j, flap=1.6):
    """(parent part, child part, hidden flaps) of a limb mask at a joint from fit_bend. As in a real arm, the outer
    corner of a bent elbow (the point of the elbow, the end of the forearm bone) belongs to the child and turns with it;
    the parent keeps its own side of a cut square to itself. The flaps are the parent's drawing continued into the inner
    crease (within flap x r of the pivot) and a thin strip past its cut on the outer side, drawn under the child, so
    turning the joint never shows a gap."""
    c = j["c"]; sp = side_of(xx, yy, c, j["ax_p"]); sc = side_of(xx, yy, c, j["ax_c"])
    if not j["bent"]:
        return mask & (sp < 0), mask & (sp >= 0), np.zeros_like(mask)
    dp = np.abs((xx - c[0]) * j["ax_p"][1] - (yy - c[1]) * j["ax_p"][0])      # distance from each centre line
    dc = np.abs((xx - c[0]) * j["ax_c"][1] - (yy - c[1]) * j["ax_c"][0])
    ap, ac = j["ax_p"], j["ax_c"]
    tp = (xx - c[0]) * ap[1] - (yy - c[1]) * ap[0]                             # signed side of the parent's centre line
    inner = np.sign(tp) == np.sign(ac[0] * ap[1] - ac[1] * ap[0])                # the side the child bends towards
    # on the inner side, only the parent's own band stays with it (the child's own edge near the pivot turns with the
    # child); on the outer side the parent keeps everything up to its cut
    parent = mask & (sp < 0) & ((sc < 0) | ~inner | ((dp <= dc) & (dp < j["r"])))
    near = np.hypot(xx - c[0], yy - c[1]) < flap * j["r"]
    crease = mask & (sp < 0) & (sc >= 0) & (dc < dp) & near & (dp < 1.05 * j["r"])   # only where both bands overlap
    # and a thin strip just past its own cut on the outer side, so the cut's far end (beyond the ball, where the limb is
    # wider than the ball) never opens a crack when the child turns
    strip = mask & ~parent & (sp >= 0) & (sp < 0.3 * j["r"]) & (sc < 0)
    return parent, mask & ~parent, crease | strip


# A limb whose top is hidden under cloth (a thigh under a wrap or skirt) is one tapered shape from its joint ball
# up under the cloth, as wide as the drawing just below the hem, so whatever comes out from under the hem as it swings
# is the same limb with continuous edges, never a block of another width or a notch where two shapes meet.
def extend_limb(shape, mask, joint, r_joint, at, length, grow=1.15):
    """joint / r_joint: the limb's ball at its lower end (a knee); at: a point on the drawn limb just below the hem;
    length: how far up from the joint the shape goes (to the hidden hip). Returns a bool mask."""
    import cv2
    H, W = shape
    c_at, r_at, _ = fit_joint(mask, tuple(at), tuple(np.subtract(at, np.subtract(joint, at))), None, cap=False)
    m = unit(np.subtract(c_at, joint)); k = length / max(np.hypot(*np.subtract(c_at, joint)), 1.0)
    r_top = float(np.clip(r_joint + (r_at - r_joint) * k, 0.9 * r_joint, grow * r_joint))
    top = np.asarray(joint, float) + m * length
    pts = [(cx + r * np.cos(a), cy + r * np.sin(a)) for (cx, cy), r in ((joint, r_joint), (top, r_top))
           for a in np.linspace(0, 2 * np.pi, 96, endpoint=False)]
    out = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(out, cv2.convexHull(np.array(pts, np.float32)).astype(np.int32), 1)
    return out.astype(bool)
