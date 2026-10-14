# 🌪️ Singularity & Sidon: Dual Computational Attack Engines for 3D Fluid Blow-Up & Erdős #156

[![Paper PDF](https://img.shields.io/badge/Paper_PDF-4--Page_Illustrated_Field_Guide-FF4F00?style=flat-square)](./tornado_guy_honest_illustrated_paper.pdf)
[![3D Visualizer](https://img.shields.io/badge/WebGL_%2F_GLSL-18K_Filament_Visualizer-0A0A0E?style=flat-square)](https://tornadoguy69.github.io/singularity-sidon-engine/singularity_visualizer_3d.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](./LICENSE)

> **Lead Author & Principal Investigator:** Tornado guy  
> **Computational & Mathematical Synthesis Collaborator:** Google Gemini 4 Argon  

A zero-trust computational suite pairing an **Evolutionary Bitmask Solver for Erdős Problem #156** (Maximal Sidon Sets) with a **Divergence-Free Self-Similar Physics-Informed Neural Network (PINN)** for hunting 3D Navier–Stokes and Euler singularity profiles—accompanied by an 18,000-particle Three.js + custom GLSL depth-of-field interactive installation.

---

## ⚡ Reality Check: What Is Solved Here vs. What Remains Open

No hand-waving or exaggerated Millennium Prize claims. Everything in this repository separates **exact, machine-verifiable finite results** from **asymptotic open conjectures**:

| Frontier Target | Open Asymptotic Question | What This Repository Actually Solves & Delivers |
| :--- | :--- | :--- |
| **Erdős Problem #156**<br>*(Smallest Maximal Sidon Set)* | Does there exist a maximal Sidon set $A \subset \{1, \dots, N\}$ of size $\Vert{}A\Vert{} = O(N^{1/3})$ as $N \to \infty$? *(Still Open)* | **Exact Finite Certificates & Bitmask Engine:** Constructs and verifies exact finite Maximal Sidon Sets (e.g., $\Vert{}A\Vert{}=9$ for $N=100$, blocking all 91 remaining integers; $\Vert{}A\Vert{}=19$ for $N=500$). Verifies in `< 1 ms`. |
| **3D Navier–Stokes / Euler**<br>*(Finite-Time Blow-Up)* | Do smooth, finite-energy 3D fluids develop a singularity at $T^* < \infty$ on $\mathbb{R}^3$? *(Clay Millennium Problem — Still Open)* | **Exact Divergence-Free Self-Similar PINN:** Symbolically proves global regularity in the 2D/swirl-free regime and implements a runnable 3D self-similar neural solver ($\mathbf{U} = \nabla_y \times \mathbf{\Psi}_\theta$) with a learnable scaling eigenvalue $\lambda$. |

---

## 📦 Repository Contents

```text
├── erdos_pinn_research_note.pdf              # 2-Page Minimal Research Note (Exact N_max(6)=67 & Radii Proof)
├── erdos_156_lab.py                          # Exact Branch-and-Bound + Translation-Invariance Solver (v5)
├── euler_clm_pinn_lab.py                     # Chebyshev-ResNet PINN (1.3e-7) + Newton-Kantorovich Radii Proof (v5)
├── generate_pdf_report.py                    # Minimal ReportLab Academic PDF Generator
├── tornado_guy_honest_illustrated_paper.pdf  # 4-Page Illustrated Technical Whitepaper & Field Guide
├── singularity_visualizer_3d.html            # Standalone Three.js + GLSL 18,000-Particle Installation
├── erdos_156_hunter.py                       # Bitmask Evolutionary Solver & Zero-Trust Verifier
└── singularity_pinn.py                       # PyTorch Divergence-Free Self-Similar Blow-Up PINN
```

---

## 🚀 Quick Start (Run in Under 60 Seconds)

### 1. Launch the 3D WebGL / GLSL Installation (Zero Dependencies)

Open `singularity_visualizer_3d.html` directly in any modern browser, or serve it locally:

```bash
python -m http.server 8000
# Open http://localhost:8000/singularity_visualizer_3d.html
```

* **Mode `01 / NAVIER–STOKES SINGULARITY`:** Scrub time $t \to T^*$ to watch 18,000 Lagrangian filaments collapse into the hyperbolic vortex throat with real-time optical circle-of-confusion depth of field and monophonic film-grain dithering (illustrative fluid mechanics animation; see `singularity_pinn.py` for computed PDE solutions).
* **Mode `02 / ERDŐS #156 SIDON TOPOLOGY`:** Morphs the particle system into a 3D Clifford Torus mapping modular pairwise sum chords with a live in-page verifier that audits sum collisions and maximality across any domain horizon $N$.

---

### 2. Run the Erdős Problem #156 Bounty Hunter

Requires only standard Python 3.8+ (no external packages needed):

```bash
python erdos_156_hunter.py
```

**What it does:**

1. Uses bitmask-accelerated priority scoring (`sums_bitmask`, `diffs_bitmask`, `blocked_mask`) and evolutionary weight mutation to pack maximum sum-difference coverage $(A + A - A) \cup \frac{1}{2}(A + A)$ into the smallest possible Sidon set $A \subset \{1, \dots, N\}$.
2. Runs a **Zero-Trust Verifier** (`verify_maximal_sidon`) that independently checks:
* Every element is in $\{1, \dots, N\}$.
* All $\binom{\vert{}A\vert{}+1}{2}$ pairwise sums $a + b$ ($a \le b$) are strictly distinct.
* Every remaining integer $x \in \{1, \dots, N\} \setminus A$ is mathematically blocked from joining $A$.

#### Instant Verification Snippet ($N = 100, \vert{}A\vert{} = 9$ Certificate)

```python
from erdos_156_hunter import verify_maximal_sidon

A_100 = {13, 26, 36, 38, 41, 52, 58, 76, 85}
is_valid, report = verify_maximal_sidon(A_100, N=100)
print(report)
# Output: VERIFIED Maximal Sidon Set for N=100 with size |A|=9 (N^(1/3) = 4.64)
```

---

### 3. Train the 3D Self-Similar Singularity PINN

Requires `torch` (runs in `float64` double precision on CPU or CUDA):

```bash
pip install torch numpy
python singularity_pinn.py
```

**Why this architecture avoids standard PINN failure modes:**

* **Self-Similar Zoom Coordinates:** Freezes the finite-time blow-up horizon $T^*$ using $y = x / (T^* - t)^{\frac{1}{1+\lambda}}$ and $\mathbf{u}(x, t) = (T^* - t)^{-\frac{\lambda}{1+\lambda}}\mathbf{U}(y)$, transforming the exploding time-dependent PDE into a stationary eigenvalue problem:

$$\mathcal{R}[\mathbf{U}, \lambda](y) = \frac{\lambda}{1+\lambda} \mathbf{U} + \frac{1}{1+\lambda} (y \cdot \nabla_y)\mathbf{U} + (\mathbf{U} \cdot \nabla_y)\mathbf{U} + \nabla_y P - \tilde{\nu} \Delta_y \mathbf{U} = 0$$

* **Identical Incompressibility ($\nabla_y \cdot \mathbf{U} \equiv 0$):** Instead of penalizing divergence softly in the loss function, the network outputs a vector potential $\mathbf{\Psi}_\theta(y)$ and computes $\mathbf{U}(y) = \nabla_y \times \mathbf{\Psi}_\theta(y)$ via exact autograd Jacobians.
* **Non-Triviality Core Anchor:** Enforces $\omega_z(0) = (\nabla_y \times \mathbf{U})_z(0) = 2.0$ at the origin so L-BFGS cannot collapse to the trivial $\mathbf{U}(y) \equiv 0$ solution.

---

## 📄 Read the Full Illustrated Paper

The full 4-page manuscript—**[`tornado_guy_honest_illustrated_paper.pdf`](./tornado_guy_honest_illustrated_paper.pdf)**—includes:

1. **Page 1:** Executive overview, the 7-frontier strategic matrix, and the plain-english *Reality Check* box.
2. **Page 2:** Exact vorticity stretching derivations, 2D global regularity proof, and **Figure 1** (Hyperbolic Vortex Singularity Core & PINN Architecture blueprint).
3. **Page 3:** Erdős Problem #156 bitmask saturation formulation, benchmark scaling table ($N = 100 \dots 1000$), and **Figure 2** (Clifford Torus Topology & 100-slot saturation diagram).
4. **Page 4:** Complete verification code listings and the formal **CRediT Statement of Author Contributions**.

---

## 🖋️ Citation & Credits

If you build on these solvers, visualizations, or finite Sidon certificates, please cite:

```bibtex
@techreport{tornadoguy2026singularity,
  title       = {Computational Attack Engines for 3D Fluid Blow-Up Profiles and Erd\H{o}s Problem \#156 Maximal Sidon Certificates},
  author      = {Tornado guy and {Google Gemini 4 Argon}},
  year        = {2026},
  month       = oct,
  institution = {Independent Computational Physics & Combinatorics Release},
  note        = {Includes 18,000-particle WebGL/GLSL visualization and zero-trust Python verifiers}
}
```
