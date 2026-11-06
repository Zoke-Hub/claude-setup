# Paper-puppet runtime: draw a rig in any pose, walk it with planted feet, push cloth, draw the paper edge, check frames.
# A rig is a folder with one RGBA PNG per piece (full source resolution, cropped to its box) and rig.json:
#   {"size": [W, H], "joints": {name: [x, y]}, "radii": {name: r}, "rim": {"rgb": [r, g, b], "width_px": 24},
#    "pieces": {name: {"x", "y", "w", "h", "pivot", "joint", "parent", "z"}},
#    "feet": {"F": [[heel], [toe]], "B": [...]},                       (flat feet, walkers only)
#    "hem": {"cloth": piece, "line": [[x, y], [x, y]], "below": [x, y], "limbs": [pieces]},   (limbs under cloth)
#    "keep_drawing": [cloth and prop pieces]}
# Joint names used by the walk: hip, kneeF / kneeB, ankleF / ankleB; leg pieces thighF / shinF / footF (and B).
# Transforms are 3x3 matrices from source pixels to world pixels; a pose is {piece: matrix}.
import json, math, os
import cv2
import numpy as np


def T(x, y): return np.array([[1, 0, x], [0, 1, y], [0, 0, 1.0]])
def R(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
def about(p, deg): return T(*p) @ R(deg) @ T(*-np.asarray(p))
def rot2(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])
def ang(v): return math.degrees(math.atan2(v[1], v[0]))
def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def glide(f, keys, start=0.0):
    """eased (no overshoot) value over frames: keys = [(start_frame, value, duration), ...]"""
    v = start
    for k0, val, d in keys:
        if f >= k0: x = min((f - k0) / d, 1.0); v = v + (val - v) * (x * x * x * (x * (6 * x - 15) + 10))
    return v


class Puppet:
    def __init__(self, rigdir, scale):
        self.S = scale
        self.rig = json.load(open(os.path.join(rigdir, "rig.json")))
        self.J = {k: np.array(v, float) for k, v in self.rig["joints"].items()}; self.R = self.rig["radii"]
        self.rim = np.array(self.rig["rim"]["rgb"], np.float32) / 255; self.rim_w = self.rig["rim"]["width_px"] * scale
        self.pieces = {}
        for k, p in self.rig["pieces"].items():
            im = cv2.imread(os.path.join(rigdir, k + ".png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
            rgb = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2RGB); a = im[..., 3:4]
            w, h = max(1, round(p["w"] * scale)), max(1, round(p["h"] * scale))
            self.pieces[k] = dict(img=cv2.resize(np.dstack([rgb * a, a]), (w, h), interpolation=cv2.INTER_AREA), x=p["x"], y=p["y"], z=p["z"])

    def draw(self, layer, k, Mw):
        """composite piece k (premultiplied) into layer with world->canvas matrix Mw"""
        pc = self.pieces[k]; img = pc["img"]; h, w = img.shape[:2]; LH, LW = layer.shape[:2]
        A = Mw @ T(pc["x"], pc["y"]) @ np.diag([1 / self.S, 1 / self.S, 1])
        cs = A @ np.array([[0, w, 0, w], [0, 0, h, h], [1, 1, 1, 1.0]])
        x0, y0 = np.floor(cs[:2].min(1)).astype(int) - 2; x1, y1 = np.ceil(cs[:2].max(1)).astype(int) + 2
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, LW), min(y1, LH)
        if x1 <= x0 or y1 <= y0: return
        wp = cv2.warpAffine(img, (T(-x0, -y0) @ A)[:2], (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        roi = layer[y0:y1, x0:x1]; roi[:] = wp + roi * (1 - wp[..., 3:4])

    def layer(self, M, W2C, size):
        """all pieces back to front; W2C = world -> canvas (camera and scale). Limbs listed under a cloth's hem show only
        below that cloth's hem line (in After Effects: a track matte parented to the cloth)."""
        L = np.zeros((size[1], size[0], 4), np.float32); hem = self.rig.get("hem")
        for k in sorted(self.pieces, key=lambda k: self.pieces[k]["z"]):
            if hem and k in hem["limbs"]:
                tmp = np.zeros_like(L); self.draw(tmp, k, W2C @ M[k])
                A = W2C @ M[hem["cloth"]]; (x1, y1), (x2, y2) = [(A @ np.array([*p, 1.0]))[:2] for p in hem["line"]]
                bx, by = (A @ np.array([*hem["below"], 1.0]))[:2]
                yy, xx = np.mgrid[0:size[1], 0:size[0]]
                sd = lambda px, py: (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
                m = np.clip(sd(xx, yy) * np.sign(sd(bx, by)) / np.hypot(x2 - x1, y2 - y1) + 0.5, 0, 1)[..., None]
                tmp *= m; L[:] = tmp + L * (1 - tmp[..., 3:4])
            else: self.draw(L, k, W2C @ M[k])
        return L

    def edge(self, L):
        """the paper edge: one pale rim round the whole silhouette (outside only), as an alpha"""
        k = int(round(self.rim_w)); ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))
        return cv2.GaussianBlur(cv2.dilate(L[..., 3], ker), (0, 0), 0.8)


def composite(P, L, background):
    """background (H, W, 3, 0..1) + paper edge + puppet layer"""
    rim = P.edge(L)
    img = background * (1 - rim[..., None]) + P.rim * rim[..., None]
    return L[..., :3] + img * (1 - L[..., 3:4])


class Gait:
    """Planted feet: heel strike (rock on the heel), flat, heel-off (rock on the toe), swing; the hip bobs twice a
    cycle. Feet stay flat in the swing (no toe curl). Units are source pixels; y up is negative.
    ncyc: frames per cycle (two steps); stride: hip travel per cycle; foot_back: where each foot lands relative to the
    hip; bob: hip rise and fall; lift: swing foot height; hip_drop: how far the hip sits below a straight leg (knee bend)."""
    HS, TO = -9.0, 24.0                       # heel-strike and toe-off angles: gentle, so a leg never folds above the foot

    def __init__(self, P, ncyc, stride, foot_back, bob, lift, hip_drop, ph0=0.0, feet=None):
        self.P, self.N, self.stride, self.back, self.bob, self.lift, self.ph0 = P, ncyc, stride, foot_back, bob, lift, ph0
        J = P.J; hip = J["hip"]; self.L = {}
        feet = P.rig.get("feet", feet)
        for s_, off in (("F", 0.0), ("B", 0.5)):
            knee, ankle = J["knee" + s_], J["ankle" + s_]; heel, toe = feet[s_]
            rest = ang(np.subtract(toe, heel))
            hf, tf = rot2(np.subtract(heel, ankle), -rest), rot2(np.subtract(toe, ankle), -rest)
            self.L[s_] = dict(knee=knee, ankle=ankle, L1=np.linalg.norm(knee - hip), L2=np.linalg.norm(ankle - knee), rest=rest,
                              hf=hf, tf=tf, hA=(hf[1] + tf[1]) / 2, off=off, shin0=ang(ankle - knee), thigh0=ang(knee - hip))
        LF = self.L["F"]; self.hipH = LF["L1"] + LF["L2"] - hip_drop + LF["hA"]

    def ph(self, f, off=0.0): return f / self.N + self.ph0 + off
    def hip_x(self, f): return self.stride / self.N * f
    def hip_y(self, f): return -self.hipH + self.bob * math.cos(4 * math.pi * (self.ph(f) - 0.05))
    def heel_x0(self, L, k): return self.hip_x(((k + 0.30) - self.ph0 - L["off"]) * self.N) + L["hf"][0] + self.back

    def foot(self, L, f):
        p = self.ph(f, L["off"]); k = math.floor(p); u = p - k; X0 = self.heel_x0(L, k); hf, tf = L["hf"], L["tf"]
        def strike(x0, a): return np.array([x0, 0.0]) + rot2(-hf, a), a
        def toeoff(x0, a): return np.array([x0 + tf[0] - hf[0], 0.0]) + rot2(-tf, a), a
        if u < 0.10: return strike(X0, self.HS * (1 - smooth(u / 0.10)))
        if u < 0.38: return strike(X0, 0.0)
        if u < 0.62: return toeoff(X0, self.TO * smooth((u - 0.38) / 0.24))
        w = (u - 0.62) / 0.38; a0, p0 = toeoff(X0, self.TO); a1, p1 = strike(self.heel_x0(L, k + 1), self.HS); e = smooth(w)
        pos = np.array([a0[0] + (a1[0] - a0[0]) * e, a0[1] + (a1[1] - a0[1]) * w - self.lift * math.sin(math.pi * w) ** 1.2])
        return pos, p0 + (p1 - p0) * smooth(w * 1.15)

    @staticmethod
    def ik(H, A, L1, L2):                      # two-bone IK, the knee bends forward (+x)
        d = A - H; dist = min(np.linalg.norm(d), L1 + L2 - 1.0)
        a = math.acos(max(-1, min(1, (L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist))))
        b = math.atan2(d[1], d[0]); K = H + L1 * np.array([math.cos(b - a), math.sin(b - a)])
        return K, K + L2 * (A - K) / np.linalg.norm(A - K)

    def legs(self, M, Hw, f, with_thigh=True):
        """add thigh (if the rig has one), shin and foot transforms for frame f, hip at world point Hw"""
        J = self.P.J
        for s_ in ("F", "B"):
            L = self.L[s_]; A, p = self.foot(L, f); K, Ae = self.ik(Hw, A, L["L1"], L["L2"])
            if with_thigh: M["thigh" + s_] = T(*Hw) @ R(ang(K - Hw) - L["thigh0"]) @ T(*-J["hip"])
            M["shin" + s_] = T(*K) @ R(ang(Ae - K) - L["shin0"]) @ T(*-L["knee"])
            M["foot" + s_] = T(*Ae) @ R(p - L["rest"]) @ T(*-L["ankle"])


def push_cloth(M, piece, pivot, base, edge_pt, probes, reach, parent="body", cap=-3.0, margin=60):
    """turn a cloth piece about its pivot just enough that its front edge stays ahead of every probe (points on the limbs
    under it, in each limb's source space), never more than cap degrees: cloth is nudged by the limb under it"""
    def gap(a):
        edge = ((M[parent] @ about(pivot, a)) @ np.array([*edge_pt, 1.0]))[0] - margin
        return max((M[pc] @ np.array([*pt, 1.0]))[0] for pc, pt in probes) - edge
    push = 0.0
    for _ in range(5):
        g = gap(base + push)
        if g <= 0: break
        push -= math.degrees(g / reach)
    M[piece] = M[parent] @ about(pivot, base + max(push, cap))


def qa(P, pose, frames, W2C_of, size, min_cover=0.995):
    """Check every frame: the silhouette is one connected shape, and every joint circle (85 % of its radius) is fully
    covered. pose(f) -> M; W2C_of(f, M) -> world->canvas matrix. Returns (worst cover, [(frame, pieces, cover, joint)])."""
    child = {p["joint"]: k for k, p in P.rig["pieces"].items() if p.get("parent")}
    joints = [j for j in P.R if j in child and j in P.J]
    bad, worst = [], 1.0
    for f in frames:
        M = pose(f); W2C = W2C_of(f, M); L = P.layer(M, W2C, size); a = (L[..., 3] > 0.5).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(a, connectivity=8); big = int((st[1:, cv2.CC_STAT_AREA] > 30).sum())
        cov = {}
        for j in joints:
            c = (W2C @ M[child[j]] @ np.array([*P.J[j], 1.0]))[:2]; r = P.R[j] * P.S * 0.85
            m = np.zeros_like(a); cv2.circle(m, (int(round(c[0])), int(round(c[1]))), max(int(r), 1), 1, -1)
            if m.any(): cov[j] = float(a[m > 0].mean())
        lo = min(cov.values()) if cov else 1.0; worst = min(worst, lo)
        if big != 1 or lo < min_cover: bad.append((f, big, round(lo, 3), min(cov, key=cov.get) if cov else ""))
    return worst, bad


def rest_compare(rigdir, drawing, scale=0.5, out=None):
    """At its own pose a puppet must be exactly the drawing. Renders the rig with every piece at rest and compares its
    silhouette with the drawing (pale paper rim stripped): returns (px bulging past the drawn outline, px of the drawing
    missing), at `scale`; with `out`, saves a map (grey = drawing, red = bulges, blue = missing). Run before every render;
    the only differences should be ones the reviewer asked for (a replaced foot, a redrawn edge)."""
    from PIL import Image
    P = Puppet(rigdir, scale); W, H = P.rig["size"]
    L = P.layer({k: np.eye(3) for k in P.pieces}, np.diag([scale, scale, 1.0]), (int(W * scale), int(H * scale)))
    r = L[..., 3] > 0.5
    a = np.asarray(Image.open(drawing)).astype(np.float32); al = a[..., 3] / 255; fig = al > 0.5
    inset = cv2.distanceTransform(fig.astype(np.uint8), cv2.DIST_L2, 5)
    creamy = np.clip(((a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)) - 110) / 90, 0, 1)
    core = (al * (1 - creamy * np.clip((40 - inset) / 6, 0, 1))) > 0.5
    c = cv2.resize(core.astype(np.uint8), (r.shape[1], r.shape[0]), interpolation=cv2.INTER_AREA).astype(bool)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    bulge = r & ~cv2.dilate(c.astype(np.uint8), k).astype(bool); miss = c & ~cv2.dilate(r.astype(np.uint8), k).astype(bool)
    if out:
        vis = np.full(c.shape + (3,), 235, np.uint8); vis[c] = (170, 170, 170); vis[r & c] = (90, 90, 90)
        vis[cv2.dilate(bulge.astype(np.uint8), k).astype(bool)] = (0, 0, 255); vis[cv2.dilate(miss.astype(np.uint8), k).astype(bool)] = (255, 80, 0)
        cv2.imwrite(out, vis)
    return int(bulge.sum()), int(miss.sum())
