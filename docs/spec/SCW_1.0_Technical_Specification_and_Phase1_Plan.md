# SCW 1.0 — Scientific Computing Workbench
## 正式技術規格與第一階段實作計畫

- 文件版本：1.0-draft
- 狀態：供專案啟動與架構基線使用
- 技術方向：Python 科學計算工具鏈
- 架構：模組化單體（Modular Monolith）
- 介面：Python API + CLI + Jupyter
- 數學核心：自行設計數學抽象，底層使用 NumPy / SciPy
- Repository：單一 Repository（Monorepo）

---

## 1. 專案摘要

SCW（Scientific Computing Workbench）是一套以 Python 為核心的個人科學計算工作台。它整合數學抽象、數值演算法、符號運算介接、視覺化、實驗重現、測試與文件工具，讓數學與物理研究能在一致、可測試、可擴充的環境中進行。

**1.0 的目標不是一次完成所有科學功能，而是建立可靠的工程骨架與第一批數學核心。**

### 1.1 設計目標

1. 數學語意清楚：Vector、Covector、Matrix、LinearMap 等概念不混為單純 ndarray。
2. 模組邊界穩定：數學核心不依賴 CLI、Jupyter 或繪圖套件。
3. 可驗證：每個核心運算都有單元測試、性質測試及參考實作比較。
4. 可重現：鎖定依賴、記錄版本與測試環境。
5. 可漸進擴充：後續加入 Tensor、Differential Geometry、ODE/PDE、Physics Simulation。
6. 優先採用成熟底層函式庫，不為了「全部自己寫」而重造低階數值核心。

### 1.2 非目標（1.0 不做）

- 不做微服務、分散式計算或雲端多租戶。
- 不做完整桌面 GUI 或 Web IDE。
- 不自行取代 NumPy / SciPy 的高效能底層線性代數。
- 不承諾完整的形式化定理證明系統。
- 不在第一階段實作完整 Tensor Calculus、Manifold 或 PDE 求解器。

---

## 2. 架構決策與原則

| 項目 | 決策 |
|---|---|
| 系統架構 | 模組化單體 |
| 使用介面 | Python API、CLI、Jupyter |
| 數學核心 | 自行定義語意與型別，NumPy / SciPy 負責底層數值運算 |
| Repository | 單一 Git Repository |
| 套件布局 | `src/` layout |
| Python 版本 | Python 3.12+；CI 至少測試 3.12、3.13 |
| 依賴管理 | uv + `uv.lock` |
| 品質工具 | Ruff、pytest、Hypothesis、pre-commit |
| 文件 | MkDocs Material |
| CI | GitHub Actions |

### 2.1 分層架構

```text
┌─────────────────────────────────────────────────────┐
│                  User Interfaces                    │
│           Python API | CLI | Jupyter                │
├─────────────────────────────────────────────────────┤
│                 Application Layer                   │
│       use cases | workflows | experiment runner     │
├─────────────────────────────────────────────────────┤
│                   Domain Layer                      │
│  Vector | Covector | Matrix | LinearMap | Spaces     │
├─────────────────────────────────────────────────────┤
│               Numerical Infrastructure              │
│            NumPy | SciPy | optional backends          │
├─────────────────────────────────────────────────────┤
│              Quality & Documentation                │
│       pytest | Hypothesis | Ruff | MkDocs | CI        │
└─────────────────────────────────────────────────────┘
```

**依賴方向規則：** Domain Layer 不得依賴 CLI、Jupyter、Matplotlib 或檔案系統。介面層呼叫應用層；應用層使用領域物件與計算服務；底層數值套件由領域實作或 adapter 封裝。

### 2.2 模組邊界

- `math_core`：數學物件、空間、代數操作與數學不變量。
- `numerical`：數值演算法；可接受 `math_core` 定義的輸入，但不得反向污染領域模型。
- `symbolic`：SymPy adapter，非數學核心的必要依賴。
- `visualization`：繪圖與視覺化 adapter。
- `physics`：物理模型與方程式，使用 math/numerical API。
- `experiments`：實驗設定、執行紀錄與結果索引。
- `cli`：命令列入口，只負責解析參數與呼叫應用服務。

---

## 3. Repository 目錄規格

```text
scientific-computing-workbench/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── .pre-commit-config.yaml
├── mkdocs.yml
│
├── src/
│   └── scw/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── exceptions.py
│       ├── math_core/
│       │   ├── __init__.py
│       │   ├── spaces.py
│       │   ├── vector.py
│       │   ├── covector.py
│       │   ├── matrix.py
│       │   └── linear_map.py
│       ├── numerical/
│       │   ├── __init__.py
│       │   └── linalg.py
│       ├── symbolic/
│       │   └── __init__.py
│       ├── visualization/
│       │   └── __init__.py
│       ├── physics/
│       │   └── __init__.py
│       ├── experiments/
│       │   └── __init__.py
│       └── cli/
│           ├── __init__.py
│           └── app.py
│
├── tests/
│   ├── unit/
│   │   ├── test_vector.py
│   │   ├── test_covector.py
│   │   ├── test_matrix.py
│   │   └── test_linear_map.py
│   ├── property/
│   │   └── test_vector_properties.py
│   ├── integration/
│   │   └── test_public_api.py
│   └── conftest.py
│
├── examples/
│   ├── 01_vectors_and_covectors.py
│   └── 02_matrix_operations.py
├── notebooks/
│   └── 01_scw_quickstart.ipynb
├── docs/
│   ├── index.md
│   ├── architecture/
│   │   └── decisions.md
│   ├── mathematics/
│   │   └── vector-spaces.md
│   └── tutorials/
│       └── quickstart.md
├── benchmarks/
└── scripts/
```

目錄可隨模組成熟而擴充；不要為尚未實作的子系統建立大量空目錄。上列結構是目標布局，Phase 1 只需建立已排定模組。

---

## 4. 技術堆疊與依賴策略

### 4.1 核心依賴

| 套件 | 用途 | 分類 |
|---|---|---|
| NumPy | ndarray、向量化與基礎線性代數 | runtime |
| SciPy | 數值線性代數與科學演算法 | runtime |
| Typer | CLI 介面 | runtime |
| Pydantic | 設定與外部輸入驗證（必要時使用） | runtime |
| SymPy | 符號數學整合 | optional |
| Matplotlib | 2D 繪圖 | optional |
| JupyterLab | 互動研究環境 | dev |
| pytest | 測試 | dev |
| pytest-cov | 覆蓋率 | dev |
| Hypothesis | 性質導向測試 | dev |
| Ruff | lint / format | dev |
| mypy | 靜態型別檢查 | dev |
| MkDocs Material | 文件網站 | dev |
| pre-commit | 提交前品質檢查 | dev |

避免把所有未來可能用到的套件放入核心依賴。使用 optional dependency groups，保持最小安裝體積。

### 4.2 建議 `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "scw"
version = "0.1.0"
description = "Scientific Computing Workbench"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
dependencies = [
  "numpy>=2.0",
  "scipy>=1.13",
  "typer>=0.12",
]

[project.optional-dependencies]
symbolic = ["sympy>=1.13"]
visualization = ["matplotlib>=3.9"]
notebook = ["jupyterlab>=4.2", "ipykernel>=6.29"]
dev = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
  "hypothesis>=6.100",
  "ruff>=0.6",
  "mypy>=1.11",
  "pre-commit>=3.8",
  "mkdocs-material>=9.5",
]

[project.scripts]
scw = "scw.cli.app:app"

[tool.hatch.build.targets.wheel]
packages = ["src/scw"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = [
  "slow: long-running tests",
  "integration: integration tests",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
check_untyped_defs = true
```

版本下限是初始相容性政策，不代表永遠固定。實際解析後由 `uv.lock` 記錄可重現的完整版本。若採用 Pydantic，應在確認設定需求後加入，不必為內部 dataclass 強制引入。

### 4.3 安裝與常用命令

```bash
uv init --package
uv add numpy scipy typer
uv add --optional symbolic sympy
uv add --optional visualization matplotlib
uv add --dev pytest pytest-cov hypothesis ruff mypy pre-commit
uv add --dev jupyterlab ipykernel mkdocs-material

uv sync --all-extras
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run scw --help
```

建議在專案初期即提交 `uv.lock`，並在 CI 使用 frozen lockfile 安裝。

---

## 5. 數學領域模型與 API 規範

### 5.1 核心設計原則

1. **語意優先：** Vector、Covector、Matrix、LinearMap 是不同概念，不以 ndarray 別名取代。
2. **維度明確：** 內積、配對、矩陣乘法等操作必須驗證維度相容。
3. **避免隱式語意：** 不讓 `*` 同時代表矩陣乘法、內積與純量乘法；必要時提供明確方法。
4. **資料安全：** 建構時複製輸入陣列，預設不暴露可變內部 buffer；提供明確的 `to_numpy(copy=True)`。
5. **數值政策清楚：** 初期使用 float64；整數、複數與任意精度策略另立設計決策。
6. **錯誤明確：** 維度錯誤、非法形狀與數值失敗使用專案例外或標準例外，並附可理解訊息。
7. **核心不綁繪圖：** Domain objects 不提供 Matplotlib figure 作為核心方法回傳值。

### 5.2 初版 API 草案

```python
from scw.math_core import Vector, Covector, Matrix, LinearMap

v = Vector([1.0, 2.0, 3.0])
w = Vector([4.0, 5.0, 6.0])

v.dimension              # 3
v.norm()                 # Euclidean norm
v.dot(w)                 # scalar

alpha = Covector([2.0, 0.0, -1.0])
alpha.evaluate(v)        # dual pairing: alpha(v)

A = Matrix([
    [1.0, 2.0],
    [3.0, 4.0],
])
A.shape                  # (2, 2)
A.apply(Vector([1.0, 1.0]))

f = LinearMap.from_matrix(A)
f.apply(Vector([1.0, 1.0]))
```

此 API 為設計目標；實作前需確認 domain/codomain 維度模型。

### 5.3 各型別責任

**Vector**
- 表示有限維實向量空間中某個已選定座標表示的向量。
- 初版保存一維數值陣列及維度。
- 支援純量乘法、加減、範數、明確的 dot product。
- 不把向量與座標基底混為一談；文件說明目前採用座標表示。

**Covector**
- 表示對偶空間元素，以線性泛函係數表示。
- `evaluate(vector)` 執行自然配對。
- 不將 Covector 與 Vector 視為同一型別，即使它們在某組基底下可用相同長度陣列表示。

**Matrix**
- 表示矩形數值陣列；矩陣作為線性映射的表示時，必須交代輸入與輸出維度。
- `@` 可保留給矩陣乘法；純量縮放使用 `*`。
- 反矩陣、分解與求解應優先提供數值服務介面；避免鼓勵使用者直接計算 inverse 解線性系統。

**LinearMap**
- 具有 domain 與 codomain 維度。
- `apply(vector)` 驗證輸入維度並回傳輸出向量。
- 內部可使用 Matrix 表示，但概念上不等同於裸矩陣。

### 5.4 精度與數值穩定性

- 預設 `float64`，並明確記錄 dtype。
- 不以精確浮點相等比較計算結果；測試使用 `numpy.testing.assert_allclose`。
- `rtol`、`atol` 由測試案例或呼叫者明確指定，避免全域魔術常數。
- 奇異矩陣、病態矩陣與非有限值（NaN/Inf）要有明確政策。
- 解線性系統優先使用 `scipy.linalg.solve` 或適當分解，不以 `inv(A) @ b` 作為標準做法。

### 5.5 公開 API 與相容性

- `scw.math_core` 是第一階段公開入口。
- 內部模組路徑在 1.0 前可調整；公開匯入路徑應集中在 `__init__.py`。
- 對公開 API 的破壞性變更記錄於 CHANGELOG。
- 版本遵循 Semantic Versioning；在 1.0 前可使用 `0.y.z`，明確標示 API 尚可能調整。

---

## 6. CLI 與 Jupyter 規範

### 6.1 CLI

第一階段只提供健康檢查與版本資訊，不把 CLI 做成另一套數學語言。

```bash
scw --help
scw version
scw doctor
```

- `version`：顯示 SCW、Python、NumPy、SciPy 版本。
- `doctor`：檢查必要依賴是否可匯入，輸出可讀診斷。
- CLI 不直接包含數學演算法；呼叫公開 Python API。

### 6.2 Jupyter

- Notebook 放在 `notebooks/`，範例放在 `examples/`。
- Notebook 只負責展示與探索；核心邏輯必須放在 `src/scw/`。
- Quickstart Notebook 必須能由乾淨環境依文件執行。
- 隨機實驗固定 seed，並顯示套件版本或環境資訊。

---

## 7. 測試與品質策略

### 7.1 測試分層

| 層級 | 目的 | 例子 |
|---|---|---|
| Unit | 單一型別與方法正確性 | Vector norm、Covector pairing |
| Property | 驗證代數性質 | 向量加法結合律、純量分配律 |
| Integration | 公開 API 協作 | LinearMap 接受 Vector 並回傳正確維度 |
| Regression | 防止已修復問題重現 | 特定浮點邊界案例 |
| Compatibility | Python/依賴版本相容 | CI 多版本測試 |

### 7.2 必測數學性質

Vector：
- \(u+v=v+u\)
- \((u+v)+w=u+(v+w)\)（在浮點容差內）
- \(a(u+v)=au+av\)
- \(\|v\|\geq 0\)
- \(\|v\|=0\) iff \(v=0\)

Covector：
- 配對對向量加法線性：\(\alpha(u+v)=\alpha(u)+\alpha(v)\)
- 配對對純量線性：\(\alpha(cv)=c\alpha(v)\)
- 不相容維度必須拒絕

LinearMap：
- \(T(u+v)=T(u)+T(v)\)
- \(T(cv)=cT(v)\)
- 輸入與輸出維度正確

Matrix：
- 形狀驗證
- 矩陣乘法維度規則
- 與 NumPy 參考結果比較

### 7.3 品質閘門

每個 PR 至少通過：
1. `ruff check .`
2. `ruff format --check .`
3. `mypy src/scw`（第一階段可先採漸進式）
4. `pytest`
5. coverage 報告

Phase 1 目標：核心數學模組測試覆蓋率至少 90%。覆蓋率不是正確性的替代品；仍需檢查邊界案例與數學性質。

---

## 8. 第一階段（Phase 1）實作計畫

### 8.1 階段目標

在四週內建立可安裝、可測試、可檢查、可文件化的專案骨架，並交付第一組可用的數學物件：Vector、Covector、Matrix、LinearMap 的最小版本。

### 8.2 工作分解

| 週次 | 任務 | 交付物 |
|---|---|---|
| Week 1 | 建立 Git Repository、src layout、pyproject、uv lock、README | 可安裝的空套件 |
| Week 1 | 建立 Ruff、pytest、GitHub Actions | PR 自動品質檢查 |
| Week 2 | 定義例外、Vector、Covector API | 核心型別初版 |
| Week 2 | 單元與性質測試 | Vector/Covector 測試 |
| Week 3 | Matrix、LinearMap 與維度規則 | 線性代數核心初版 |
| Week 3 | NumPy adapter 與數值比較測試 | 參考實作驗證 |
| Week 4 | CLI version/doctor、Quickstart 範例 | 基本操作入口 |
| Week 4 | MkDocs 文件、API 說明、Phase 1 review | 可交接的工程基線 |

### 8.3 Issue 拆分建議

- `SCW-001` Bootstrap repository and packaging
- `SCW-002` Configure uv, Ruff, pytest and pre-commit
- `SCW-003` Add GitHub Actions CI
- `SCW-004` Define domain exceptions and dtype policy
- `SCW-005` Implement Vector
- `SCW-006` Implement Covector
- `SCW-007` Implement Matrix
- `SCW-008` Implement LinearMap
- `SCW-009` Add property and integration tests
- `SCW-010` Add CLI version and doctor commands
- `SCW-011` Add MkDocs and quickstart examples
- `SCW-012` Phase 1 acceptance review

### 8.4 Definition of Done

每個功能完成前必須：
- 有型別註記與 docstring。
- 有明確的輸入、輸出及錯誤行為。
- 有單元測試；適用時有 Hypothesis 性質測試。
- 有至少一個可執行範例。
- 不違反模組依賴方向。
- Ruff 與 CI 通過。
- 公開 API 有文件。

---

## 9. Phase 1 驗收標準

Phase 1 必須同時滿足以下條件，才可標記完成。

### 9.1 專案與建置

- [ ] 新環境可用 `uv sync --all-extras` 安裝。
- [ ] `uv.lock` 已提交，CI 使用鎖定依賴。
- [ ] `uv build` 成功產生 wheel 與 source distribution。
- [ ] `src/` layout 可正常匯入 `scw`。

### 9.2 數學核心

- [ ] Vector、Covector、Matrix、LinearMap 已實作最小公開 API。
- [ ] 維度與形狀錯誤會明確失敗。
- [ ] 輸入資料不會因外部陣列後續修改而意外改變物件狀態。
- [ ] Vector 與 Covector 保持不同型別及不同語意。
- [ ] LinearMap 的 domain/codomain 維度驗證正確。

### 9.3 測試與品質

- [ ] `uv run pytest` 全數通過。
- [ ] 核心數學模組測試覆蓋率至少 90%。
- [ ] 至少涵蓋上述代數性質及維度錯誤案例。
- [ ] `ruff check .` 與 `ruff format --check .` 通過。
- [ ] CI 在 Pull Request 上自動執行。

### 9.4 使用體驗與文件

- [ ] `scw --help`、`scw version`、`scw doctor` 可執行。
- [ ] Quickstart 範例在乾淨環境可執行。
- [ ] 文件說明安裝、公開 API、測試與開發流程。
- [ ] README 清楚列出目前支援與尚未支援的功能。

---

## 10. 風險與技術債控制

| 風險 | 對策 |
|---|---|
| 過早抽象化 | 先用 Vector/Covector/Matrix 驗證抽象，再擴充 Tensor |
| 重造 NumPy/SciPy | 自己掌握數學語意與演算法介面，底層交由成熟函式庫 |
| API 過早凍結 | 0.x 版本允許調整；公開 API 集中管理 |
| 浮點測試脆弱 | 使用容差、性質測試及解析解比較 |
| 模組耦合 | Domain 不依賴 UI、Notebook 或繪圖套件 |
| 功能範圍膨脹 | Phase 1 僅完成工程骨架與有限維線性代數核心 |
| 依賴膨脹 | 核心、optional、dev 依賴分組 |

---

## 11. 後續版本方向

- **0.2：** Tensor、tensor product、contraction、基底與座標表示。
- **0.3：** Symbolic adapter、微分與積分工作流程。
- **0.4：** Numerical methods、線性系統、ODE solver。
- **0.5：** Visualization、vector field、3D plotting。
- **0.6：** Manifold、tangent/cotangent spaces、metric。
- **0.7：** Physics models 與 simulation。
- **0.8：** Experiment tracking、資料集與可重現性。
- **0.9：** API 穩定化、效能基準、文件補齊。
- **1.0：** 穩定公開 API、完整安裝與使用文件、CI 發佈流程。

版本範圍是規劃，不代表每個版本必須按日曆推出；應以驗收條件與模組成熟度決定。

---

## 12. 專案啟動後的第一個執行命令

```bash
mkdir scientific-computing-workbench
cd scientific-computing-workbench

git init
uv init --package --name scw

uv add numpy scipy typer
uv add --optional symbolic sympy
uv add --optional visualization matplotlib
uv add --dev pytest pytest-cov hypothesis ruff mypy pre-commit
uv add --dev jupyterlab ipykernel mkdocs-material

mkdir -p src/scw/math_core
mkdir -p src/scw/cli
mkdir -p tests/unit tests/property tests/integration
mkdir -p examples notebooks docs/architecture docs/mathematics docs/tutorials

git add .
git commit -m "chore: bootstrap SCW project"
```

> 注意：`uv init` 產生的初始 `pyproject.toml` 應依本規格整理；執行套件安裝後提交 `uv.lock`。CLI 入口與模組檔案需在對應任務中建立。

---

## 13. 最終決策摘要

SCW 1.0 採用模組化單體、單一 Repository、Python API + CLI + Jupyter。數學核心由專案自行定義語意與抽象，NumPy / SciPy 負責可靠的底層數值計算。第一階段以四週為規劃，交付可安裝、可測試、可持續整合的工程骨架，以及 Vector、Covector、Matrix、LinearMap 的最小實作。

**第一階段成功的標準不是功能多，而是建立一個能安全承載未來數學與科學計算功能的架構。**
