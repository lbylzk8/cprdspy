import numpy as np
import matplotlib.pyplot as plt
from clifford import Cl


def scalar(M):
    """多重向量的标量部分 (clifford 中 value[0] 即标量系数)"""
    return float(np.real(M.value[0]))


def mag(M):
    """多重向量的模长: |M| = sqrt(|<~M M>_0|)"""
    return float(np.sqrt(abs(scalar(~M * M))))


# ---------- (1) 平面转子外摆线：Cl(2) ----------
layout2, blades2 = Cl(2)
e1, e2 = blades2['e1'], blades2['e2']
I = e1 ^ e2                         # 复结构


def rotor(B, theta):
    """单位二重向量 B 张成平面内、转角 theta 的转子"""
    return (-0.5 * theta * B).exp()


def to_xy(v):
    """取出多重向量的 e1, e2 坐标 (bitmask: e1=1, e2=2)"""
    return float(np.real(v.value[1])), float(np.real(v.value[2]))


# 验证：R e1 ~R = cos(theta) e1 + sin(theta) e2
theta = 0.7
R = rotor(I, theta)
print("R e1 ~R =", R * e1 * ~R)

coeffs = [(2.0, 1, 0.0), (1.0, 3, 0.5), (0.5, -5, 1.2), (0.25, 8, 0.0)]
t = np.linspace(0, 2 * np.pi, 2000)

# (a) 逐点用 GA 计算（抽样，验证用）
pts = []
for ti in t[::50]:
    acc = 0 * e1
    for r, w, phi in coeffs:
        R = rotor(I, w * ti + phi)
        acc += r * (R * e1 * ~R)
    pts.append(to_xy(acc))
pts = np.array(pts)

# (b) 等价的 numpy 闭式（批量绘图用）
x = sum(r * np.cos(w * t + phi) for r, w, phi in coeffs)
y = sum(r * np.sin(w * t + phi) for r, w, phi in coeffs)

plt.figure(figsize=(6, 6))
plt.plot(x, y, lw=1, label='转子外摆线')
plt.plot(pts[:, 0], pts[:, 1], 'r.', ms=8, label='GA 逐点验证')
plt.axis('equal')
plt.legend()
plt.title(r'Rotor epicycles: $\sum_i r_i R_i e_1 \tilde{R}_i$')
plt.show()

# ---------- (2) 几何微积分：环面螺旋线的 κ, τ ----------
layout3, blades3 = Cl(3)
E1, E2, E3 = blades3['e1'], blades3['e2'], blades3['e3']
I3 = E1 ^ E2 ^ E3

R0, r0, omega = 2.0, 0.6, 7
s = np.linspace(0, 2 * np.pi, 1200)
X = (R0 + r0 * np.cos(omega * s)) * np.cos(s)
Y = (R0 + r0 * np.cos(omega * s)) * np.sin(s)
Z = r0 * np.sin(omega * s)


def d(q):
    return np.gradient(q, s)


vx, vy, vz = d(X), d(Y), d(Z)
ax, ay, az = d(vx), d(vy), d(vz)
jx, jy, jz = d(ax), d(ay), d(az)

kappa = np.zeros_like(s)
tau = np.zeros_like(s)
for i in range(len(s)):
    v = vx[i] * E1 + vy[i] * E2 + vz[i] * E3
    a = ax[i] * E1 + ay[i] * E2 + az[i] * E3
    da = jx[i] * E1 + jy[i] * E2 + jz[i] * E3
    B = v ^ a
    kappa[i] = mag(B) / mag(v) ** 3
    tau[i] = scalar((B ^ da) * I3.inv()) / mag(B) ** 2

fig = plt.figure(figsize=(14, 5))
ax1 = fig.add_subplot(121, projection='3d')
p = ax1.scatter(X, Y, Z, c=kappa, cmap='plasma', s=4)
ax1.set_title('环面螺旋线：按曲率 κ 着色')
fig.colorbar(p, ax=ax1, shrink=0.6, label='κ')
ax2 = fig.add_subplot(122)
ax2.plot(s, kappa, label='曲率 κ')
ax2.plot(s, tau, label='挠率 τ', alpha=0.7)
ax2.set_xlabel('s')
ax2.legend()
ax2.set_title('几何微积分：κ 与 τ')
plt.tight_layout()
plt.show()