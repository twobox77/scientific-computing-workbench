# SCW — Scientific Computing Workbench

以 Python 撰寫的**個人科學計算工作台**：在 NumPy / SciPy 之上自行定義
數學語意與型別，並以可重現、可測試的工程方式打包。

- **架構**：模組化單體（modular monolith，`src/` layout、單一 repository）。
- **介面**：Python API、CLI（Typer）、Jupyter。
- **數學核心**：SCW 定義語意與型別（Vector / Covector / Matrix / LinearMap，
  0.2 起加 Tensor / Basis）；底層數值運算交給 NumPy / SciPy。
- **Python**：3.12+（CI 測 3.12 與 3.13）。
- **授權**：MIT。

> 本檔為中文導覽，整合專案**計畫、進度與成果**，並連到所有相關文件。
> 想離線「欣賞與操作」請見 [`docs/offline.md`](docs/offline.md)。

## 目錄

- [專案計畫](#專案計畫)
- [目前進度](#目前進度)
- [成果](#成果)
- [取得與更新](#取得與更新)
- [安裝](#安裝)
- [使用](#使用)
- [欣賞與操作（離線）](#欣賞與操作離線)
- [解除安裝](#解除安裝)
- [開發](#開發)
- [授權](#授權)

## 專案計畫

正式技術規格與第一階段（Phase 1）實作計畫在
[`docs/spec/`](docs/spec/)（`SCW_1.0_Technical_Specification_and_Phase1_Plan.md`）。

- **定位**：先建立可交接的工程基線，再逐步長出數學模組；不追求一次到位。
- **依賴方向（硬規則）**：介面 → 應用層 → 領域層（`math_core`）→ 數值後端
  （NumPy / SciPy）。`math_core` 不得 import CLI、Jupyter、Matplotlib 或檔案系統。
- **版本節奏**：以**驗收條件與模組成熟度**決定，不按日曆；1.0 前用 `0.y.z`。
- **路線圖**：見規格 §11，逐版對照如下表。

## 目前進度

Phase 1 已完成並結案，逐項證據在
[Phase 1 驗收報告](docs/phase1-acceptance.md)（對照規格 §9）；一鍵重跑全部驗收：

```bash
bash scripts/verify_phase1.sh
```

各版本狀態（由 `scripts/sync_progress.py` 產生，勿手改；點版本號可看該版 release 與中文說明）：

<!-- progress:start -->
| 版本 | 里程碑內容 | 狀態 |
| --- | --- | --- |
| [0.1.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.1.0) | 工程骨架 + 數學核心（`VectorSpace` / `Vector` / `Covector` / `Matrix` / `LinearMap`） | ✅ 已發行 |
| [0.2.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.2.0) | `Tensor`、`Basis`；性質測試（Hypothesis）與回歸測試層 | ✅ 已發行 |
| [0.3.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.3.0) | `scw.symbolic`（SymPy adapter）、`einsum`、複雜度護欄 | ✅ 已發行 |
| [0.4.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.4.0) | `scw.numerical`：線性系統、分解（LU/QR/SVD/Cholesky/eigh）、ODE solver | ✅ 已發行 |
| [0.5.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.5.0) | `scw.visualization`：Matplotlib adapter（2D/3D 繪圖） | ✅ 已發行 |
| [0.6.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.6.0) | `scw.manifold`：切／餘切空間、metric、`flat` / `sharp` | ✅ 已發行 |
| [0.7.0](https://github.com/twobox77/scientific-computing-workbench/releases/tag/v0.7.0) | `scw.physics`：質點、力模型、系統與牛頓模擬 | ✅ 最新 |
| 0.8 | Experiment tracking、資料集與可重現性 | ⏳ 規劃中 |
| 0.9 | API 穩定化、效能基準、文件補齊 | ⏳ 規劃中 |
| 1.0 | 穩定公開 API、完整安裝與使用文件、CI 發佈流程 | ⏳ 規劃中 |
<!-- progress:end -->

目前已支援（摘要）：

- `scw.math_core`：`VectorSpace`、`Vector`、`Covector`、`Matrix`、`LinearMap`，
  加上 `Tensor`（order-r 陣列、外積、縮併、跡、`einsum`）與 `Basis`（座標），
  含維度／形狀驗證與唯讀資料存取。
- `scw.numerical`：`solve`、`inverse`、`det`、`lstsq`；分解 `lu`、`qr`、`svd`、
  `cholesky`、`eigh`（各附 `reconstruct`）；`solve_ivp` 解初值 ODE。
- `scw.symbolic`（optional `symbolic` extra）：`SymbolicMatrix` / `SymbolicVector`。
- `scw.visualization`（optional `visualization` extra）：Matplotlib adapter。
- `scw.manifold`：`EuclideanSpace`、`Sphere` 帶 Riemannian metric；`Metric`
  提供 `inner`、`norm` 與 `flat` / `sharp`。
- `scw.physics`：`Particle`、力模型（`ConstantForce` / `SpringForce` /
  `CentralGravity` / `Drag`）、`System`（動量與能量）與 `simulate` /
  `Trajectory` 牛頓模擬。
- CLI：`scw version`、`scw doctor`。
- 測試：單元、性質（Hypothesis）、整合、回歸四層。

尚未支援：符號微積分（積分／極限）、PDE 求解器、多體（N-body）交互作用與
剛體動力學。

變更歷史見 [`CHANGELOG.md`](CHANGELOG.md)。

## 成果

### 範例腳本（`examples/`）

| 檔案 | 內容 | 需要 extra |
| --- | --- | --- |
| [`01_vectors_and_covectors.py`](examples/01_vectors_and_covectors.py) | 向量、餘向量與自然配對 | — |
| [`02_matrix_operations.py`](examples/02_matrix_operations.py) | 矩陣、線性映射與解線性系統 | — |
| [`03_tensor_operations.py`](examples/03_tensor_operations.py) | 張量：外積、縮併與跡 | — |
| [`04_bases_and_coordinates.py`](examples/04_bases_and_coordinates.py) | 基底與座標：端到端數值流程 | — |
| [`05_symbolic_algebra.py`](examples/05_symbolic_algebra.py) | 符號線性代數（精確解，再收斂成數值） | `symbolic` |
| [`06_decompositions.py`](examples/06_decompositions.py) | 矩陣分解：LU / QR / SVD / Cholesky / eigh | — |
| [`07_ode_solving.py`](examples/07_ode_solving.py) | 常微分方程初值問題（衰減、簡諧振子） | — |
| [`08_visualization.py`](examples/08_visualization.py) | Matplotlib 繪圖，輸出 PNG 到 `scw_plots/` | `visualization` |
| [`09_manifolds.py`](examples/09_manifolds.py) | 流形：切空間、metric、`flat` / `sharp` | — |
| [`10_physics_simulation.py`](examples/10_physics_simulation.py) | 物理模擬：拋體、彈簧振子、行星軌道 | — |

### Notebook（`notebooks/`）

| 檔案 | 內容 | 需要 extra |
| --- | --- | --- |
| [`01_scw_quickstart.ipynb`](notebooks/01_scw_quickstart.ipynb) | 基礎導覽 | `notebook` |
| [`02_manifolds.ipynb`](notebooks/02_manifolds.ipynb) | 流形靜態教學（已內嵌圖，讀即可） | `notebook` |
| [`03_manifolds_interactive.ipynb`](notebooks/03_manifolds_interactive.ipynb) | 流形互動教學（3D 可拖曳） | `interactive` |

### 圖庫與文件

- **[圖庫 Gallery](docs/gallery.md)**：繪圖 adapter 能產出的每一張圖（由
  [`scripts/build_gallery.py`](scripts/build_gallery.py) 確定性重生）。
- **[文件網站](docs/)**（MkDocs Material）：數學主題（[向量空間](docs/mathematics/vector-spaces.md)、
  [數值方法](docs/mathematics/numerical-methods.md)、[符號代數](docs/mathematics/symbolic.md)、
  [視覺化](docs/mathematics/visualization.md)、[流形](docs/mathematics/manifolds.md)、
  [物理模擬](docs/mathematics/physics.md)）、
  [公開 API](docs/api.md)、[架構決策](docs/architecture/decisions.md)、
  [開發指南](docs/development.md)。
- **[離線欣賞與操作指南](docs/offline.md)**：無網路時如何安裝、欣賞、操作、解除安裝。
- **微基準**（[`benchmarks/`](benchmarks/)）：量測 SCW 相對 NumPy 的額外開銷。

## 取得與更新

**第一次**取得原始碼用 `git clone`；**之後更新一律用 `git pull`**，
不要再 clone（重複 clone 只會在當前目錄多出一份同名資料夾）。

```bash
# 第一次（只需做一次）
git clone https://github.com/twobox77/scientific-computing-workbench.git
cd scientific-computing-workbench

# 以後每次更新：進到同一份目錄，抓最新現況
cd scientific-computing-workbench
git pull
```

repo 為 **PUBLIC**，`git pull` 不需登入或 token。想先看不動檔案的遠端狀態，
可 `git fetch origin` 後 `git log --oneline origin/main -5`；若本地有未提交
變更導致 pull 被擋，用 `git stash && git pull && git stash pop`。
完整說明（含離線、用 Release 壓縮包等替代來源）見
[離線指南 §0](docs/offline.md#0-取得原始碼並進入專案目錄)。

## 安裝

```bash
uv sync --all-extras
```

只裝核心（不裝繪圖／notebook／互動）用 `uv sync`；只要特定功能用
`uv sync --extra symbolic`、`--extra visualization`、`--extra notebook` 或
`--extra interactive`。完全離線的安裝方式見
[離線指南 §0.5](docs/offline.md#05-安裝依賴一次性)。

## 使用

```python
from scw.math_core import Basis, Covector, LinearMap, Matrix, Tensor, Vector

v = Vector([1.0, 2.0, 3.0])
w = Vector([4.0, 5.0, 6.0])
v.norm()          # 歐氏範數
v.dot(w)          # 內積

alpha = Covector([2.0, 0.0, -1.0])
alpha.evaluate(v)  # 自然配對 alpha(v)

t = LinearMap.from_matrix(Matrix([[1.0, 2.0], [3.0, 4.0]]))
t.apply(Vector([1.0, 1.0]))

a = Tensor([[1.0, 2.0], [3.0, 4.0]])
a.outer(a)        # 張量積
a.contract(a)     # 縮併（此處為矩陣乘積）
float(a.trace())  # 跡

basis = Basis([Vector([1.0, 0.0]), Vector([1.0, 1.0])])
basis.to_coordinates(Vector([3.0, 2.0]))   # 在該基底下的座標
```

```bash
uv run scw version
uv run scw doctor
```

跑範例（輸出到終端機）：

```bash
uv run python examples/09_manifolds.py        # 0.6 流形：切空間、metric、flat/sharp
uv run python examples/06_decompositions.py   # 0.4 分解：LU / QR / SVD / Cholesky / eigh
uv run python benchmarks/bench_core.py
```

## 欣賞與操作（離線）

完整的離線流程（取得原始碼、安裝依賴、跑範例、開文件站、用 Jupyter 操作、
欣賞圖片）見 **[`docs/offline.md`](docs/offline.md)**。最短路徑：

```bash
uv sync --all-extras
uv run mkdocs serve -a 127.0.0.1:8000     # 瀏覽器開 http://127.0.0.1:8000
uv run jupyter lab                        # 開啟 notebooks/
```

## 解除安裝

```bash
rm -rf .venv/                             # 只移除本專案虛擬環境（最常見）
uv cache clean                            # 清 uv 快取
rm -f ~/.local/bin/uv ~/.local/bin/uvx    # 完全移除 uv 本身（無 uv self uninstall）
```

三層完整說明（專案環境 → uv 快取與受管 Python → 移除 uv）見
[離線指南 §5](docs/offline.md#5-解除安裝)。

## 開發

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run python scripts/complexity_guard.py   # 核心不得有未標註理由的逐元素迴圈
uv run pre-commit install
bash scripts/verify_phase1.sh                # 重跑 Phase 1 全部驗收
```

慣例與品質閘門見 [`CONTRIBUTING.md`](CONTRIBUTING.md)；架構與數學筆記見
[`docs/`](docs/)；給 AI agent 的倉庫知識見 [`AGENTS.md`](AGENTS.md)。

## 授權

[MIT](LICENSE)。
