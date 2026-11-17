# AGENTS.md

本檔給 AI agent 讀取，用來保存此倉庫的慣例與知識，讓不同對話之間保持一致。

## 倉庫定位

- 名稱：`twobox77/scientific-computing-workbench`（SCW，Scientific Computing Workbench）。
- 用途：以 Python 為核心的**個人科學計算工作台**。自行定義數學語意與型別
  （Vector / Covector / Matrix / LinearMap，0.2 起加 Tensor / Basis），底層數值運算交給 NumPy / SciPy。
- 架構：**模組化單體（modular monolith）**，單一 repository，`src/` layout。
- 介面：Python API、CLI（Typer）、Jupyter。
- 授權：MIT。預設分支：`main`。
- 規格來源：`docs/spec/SCW_1.0_Technical_Specification_and_Phase1_Plan.md`。
- 結案：Phase 1 驗收報告在 `docs/phase1-acceptance.md`（§9 逐項對照）；
  重跑全部驗收用 `bash scripts/verify_phase1.sh`。

## 對話前置步驟

1. 確認工作區是本 repo；若尚未 clone：
   `git clone https://$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/twobox77/scientific-computing-workbench.git .`
2. `git pull` 確保最新；remote 帶 token 並用 `GIT_TERMINAL_PROMPT=0` 執行 git 指令。
3. 讀取本檔與 `README.md`、`docs/`、規格文件，遵守其中規範。
4. 回報「已接上 repo + 已讀規則」再開始任務。

## 依賴方向（硬規則）

```
User interfaces (Python API | CLI | Jupyter)
        v
Application layer (use cases, workflows, experiment runner)
        v
Domain layer (math_core: Vector, Covector, Matrix, LinearMap, spaces)
        v
Numerical infrastructure (NumPy, SciPy, optional backends)
```

`math_core` **不得** import CLI、Jupyter、Matplotlib 或檔案系統。數值後端以
adapter 封裝，不得污染領域模型。

## 目錄結構

- `src/scw/math_core/` — 數學領域核心（公開入口 `scw.math_core`）。
- `src/scw/manifold/` — 流形幾何：`spaces.py`（`TangentSpace`/`CotangentSpace`，
  皆為 `VectorSpace` 子類，帶 `manifold`+`point`）、`metric.py`（`Metric`：
  SPD 驗證、`inner`/`norm`、`flat`/`sharp`）、`manifold.py`（`Manifold` ABC、
  `EuclideanSpace`、`Sphere`）。只依賴 `math_core` 與 `scw.exceptions`，
  **不得** import CLI/繪圖/檔案系統。
- `src/scw/physics/` — 牛頓力學：`particles.py`（`Particle`：質量 + 位置/速度
  `Vector`）、`forces.py`（`Force` ABC、`ConservativeForce` 子類、`ConstantForce` /
  `SpringForce` / `CentralGravity` / `Drag`）、`system.py`（`System` 群組粒子與力，
  回報動量/能量）、`simulation.py`（`simulate` 用 `scw.numerical.solve_ivp` 積分、
  回傳 `Trajectory`）。只依賴 `math_core` 與 `numerical`，**不得** import CLI/繪圖/
  檔案系統。積分一律委派數值層，物理層只組/拆狀態向量（`[positions..., velocities...]`）。
- `src/scw/numerical/` — 數值演算法（SciPy adapter）。
- `src/scw/symbolic/` — SymPy adapter（optional extra；只在此套件 import sympy）。
- `src/scw/visualization/` — Matplotlib adapter（optional extra；只在此套件 import matplotlib）。
- `src/scw/experiments/` — 實驗追蹤與可重現性：`records.py`（`RunRecord`/
  `Artifact` 與 `jsonable`/`canonical_json`/`derive_seed`/`environment_fingerprint`）、
  `experiment.py`（`Experiment`：設定 + 種子，`run` 產出紀錄、`rng(label)` 給可重現
  生成器、`sweep`/`with_config`/`with_seed` 回傳複本）、`store.py`（`ResultStore`：
  結果目錄，原子寫入與 `query`/`best`/`summary`）、`dataset.py`（`Dataset`：可重現
  具名欄位 + `spec`、`split`/`fingerprint`/`from_spec`）。只依賴 `math_core` 與
  `scw.exceptions`；**只有** `store.py` 碰檔案系統，其餘不得 import CLI/繪圖/檔案系統。
- `src/scw/cli/` — 命令列入口（只解析參數、呼叫公開 API，不含數學演算法）。
- `tests/{unit,property,integration,regression}/` — 單元、性質（Hypothesis）、整合、回歸測試。
- `examples/` — 可執行範例（編號排序）；每個新功能至少補一個。
- `notebooks/` — Jupyter 教學（`notebook` extra：`jupyterlab` + `ipykernel`）。
  以 `uv run jupyter lab` 開啟。`notebooks/02_manifolds.ipynb` 是 0.6 的動手玩，
  已內嵌輸出（含 3D 圖）可直接閱讀；`notebooks/03_manifolds_interactive.ipynb`
  用 ipympl（`interactive` extra）做可拖曳旋轉的 3D 圖，不預嵌輸出。改過請重跑
  `uv run jupyter nbconvert --to notebook --execute --inplace <nb>` 更新輸出。
  **注意：`ruff check .` 會 lint `.ipynb`**（cell 內程式碼視為模組），notebook
  必須 lint 乾淨，否則 CI 會掛（2026-11-16 實際踩到：commit 0de56b8 因 notebook
  的 I001/F401/E402/E702 讓 CI 紅）。修法：import 全部集中在第一個 cell、
  移除未用 import、不寫分號、函式/陳述式間留空行。
- `benchmarks/` — `timeit` 微基準，量測 SCW 相對 NumPy 的額外開銷。
- `scripts/verify_phase1.sh` — 一鍵重跑 Phase 1 全部驗收（見 `docs/phase1-acceptance.md`）。
- `docs/` — MkDocs Material 文件；`docs/spec/` 放規格正本。

## 品質閘門（每個 PR 必過）

```bash
uv run ruff check .
uv run python scripts/complexity_guard.py
uv run ruff format --check .
uv run mypy src/scw
uv run pytest --cov=scw --cov-report=term-missing
```

- **複雜度護欄**（`scripts/complexity_guard.py`，CI 已接）：核心模組不得出現
  **未標註理由的 `for`/`while` 迴圈**——逐元素迴圈是「把向量化運算改寫成 O(n) Python」
  的徵兆。若迴圈只迭代小型中介資料（basis 向量清單、einsum 下標詞）或 SymPy 純量運算，
  在迴圈上一行加 `# complexity: <理由>` 即可放行。採 **AST 靜態檢查**：決定性、瞬時、
  不需執行或追蹤（先前試過 `sys.settrace` 版本，在 pytest-cov 程序內會拖垮沙盒，已棄用）。

- 核心數學模組測試覆蓋率**至少 90%**。
- 浮點比較一律用容差（`numpy.testing.assert_allclose`），不得用精確相等。
- 公開運算必須驗證維度/形狀並明確失敗。
- 新功能需附：型別註記 + docstring、單元測試、適用時的 Hypothesis 性質測試、至少一個可執行範例。

## 測試教訓（別重蹈覆轍）

- **性質測試的浮點容差要「隨尺度」設定，別用 `np.allclose` 預設值**（2026-11-16 實際踩到）：
  比較「兩種不同捨入路徑」的結果時（如矩陣乘法結合律 `(ab)c` vs `a(bc)`），若運算元到 `1e6`，
  乘積可達 `1e18`、災難性消去使誤差膨脹到 `~1e-8`，**超過 `np.allclose` 預設 `atol=1e-8`**，
  於是**本機過、CI 掛**（RNG 不同）。解法：定律類性質測試用 `rtol=1e-9, atol=1e-6`
  （`np.testing.assert_allclose`），並把運算元範圍壓到 `|x|<=1e3` 以内使條件數良好；
  只有「只需有限性／非負性」的性質（如 norm）才保留寬範圍 `1e6`。
  **驗證方式**：改完用多個 `--hypothesis-seed` 跑，並用大樣本 sweep 量測實際最大誤差
  （實測結合律最壞 `9.3e-10`，對 `atol=1e-6` 有 ~1000× 餘裕）。
- **回歸測試層**（`tests/regression/`）專門釘住「已修過的數值邊界案例」：
  norm 下溢／上溢、防禦性複製、唯讀視圖、非有限值拒絕、Covector 與 Vector 型別分離。
  修好一個 bug 就補一條，避免日後悄悄壞掉（規格 §7.1 明列此層）。

## 開發慣例

- 依賴管理：`uv`（提交 `uv.lock`，CI 用 `--frozen` 安裝）。
- **更新既有工作區一律 `git pull`，不要重新 `git clone`**。clone 只在首次取得時用；
  重複 clone 會在當前目錄多出同名資料夾（使用者 2026-11-16 實際踩到）。此規則寫在
  `README.md` 的「取得與更新」與 `docs/offline.md` §0。
- **`.pre-commit-config.yaml` 的 `ruff-pre-commit` rev 必須與 `uv.lock` 的 ruff 版本一致**。
  曾因 pre-commit 釘舊版（v0.6.9）而 uv.lock 是新版（0.17.5），在乾淨的樹上
  `pre-commit run --all-files` 冒出 `UP038`，CI 卻過——版本落差會製造假失敗。
  升 ruff 時兩處一起改。
- **`uv sync --extra <x>` 會移除其他 extra 與 dev 依賴**（2026-11-16 踩到：跑完
  `uv sync --extra interactive` 後 `ruff` 不見了）。要保留全套請用
  `uv sync --all-extras`。CI 用 `--all-extras --frozen`。
- Extras：`symbolic`、`visualization`、`notebook`、`interactive`（後者 =
  matplotlib + jupyterlab + ipykernel + ipympl，供可拖曳 3D）、`dev`。
- 版本：Semantic Versioning；1.0 前用 `0.y.z`，破壞性變更記錄於 `CHANGELOG.md`。
- 直接 commit 進 `main`（不開 PR），除非另有指示。
- 公開 API 集中由 `__init__.py` 匯出；內部模組路徑在 1.0 前可調整。

## 路線圖（規格 §11）

0.2 Tensor → 0.3 Symbolic → 0.4 Numerical/ODE → 0.5 Visualization →
0.6 Manifold → 0.7 Physics → 0.8 Experiments → 0.9 API 穩定化 → 1.0 穩定。
版本以驗收條件與模組成熟度決定，不按日曆。

## 設計備忘

- **切空間用 dataclass 繼承，不用 wrapper**（0.6）：`TangentSpace`/`CotangentSpace`
  直接 `@dataclass(frozen=True, kw_only=True)` 繼承 `VectorSpace`，多帶
  `manifold`+`point` 兩個欄位。`kw_only=True` 是必須的——否則子類欄位沒有預設值
  會撞上父類有預設值的欄位（`name`），dataclass 會直接 `TypeError`。因為「點」
  進入空間的 `__eq__`/`__hash__`，不同點的切向量自然被既有的 space 檢查擋下，
  不必另外寫驗證。回顧：曾考慮 wrapper（Approach B），但會失去「切向量就是
  `Vector`」的互通性。
- **`Manifold` ABC 的 `dimension` 用純註解、不掛 `@property @abstractmethod`**：
  若父類把 `dimension` 定義成抽象 property，子類就無法用 dataclass 欄位實作它
  （`TypeError: Can't instantiate abstract class`）。改法：父類只寫
  `dimension: int` 註解（mypy 看得到型別），子類用 `field(init=False, default=...)`
  提供值。mypy 另會抱怨「writeable attribute 被 read-only property 覆寫」，這也是
  不用 property 的理由之一。
- **`Metric.norm` 走 Cholesky 因式**：`G = L L^T`，長度取 `|L^T v|`，避免對 `G`
  直接開平方而把條件數平方。

### 已完成的里程碑

- **0.2** Tensor / Basis。
- **0.3** `scw.symbolic`（SymPy adapter，optional extra）、`einsum`。
- **0.4** `scw.numerical` 數值層：`lstsq`；分解 `lu`/`qr`/`svd`/`cholesky`/`eigh`
  （每個結果都有 `reconstruct`，`SVDResult.rank` 隨尺度取容差）；`solve_ivp` +
  `ODESolution` 包裝 `scipy.integrate.solve_ivp`（RHS 以 `(t, Vector) -> Vector`
  書寫，`METHODS` 列出可用積分器，支援 `t_eval`/`rtol`/`atol`/`dense_output`）。
  新例外：`NumericalError`（`ValueError`）、`ConvergenceError`（`RuntimeError`）。
  範例 `06_decompositions.py`、`07_ode_solving.py`。
- **0.5** `scw.visualization` Matplotlib adapter（optional extra）：2D 的
  `plot_vector`/`plot_vectors`/`plot_function`/`plot_vector_field`（`normalize`）/
  `plot_matrix`（熱圖，可選 colorbar 與格值標註）/`plot_ode_solution`；3D 的
  `new_3d_figure`/`plot_vectors_3d`/`plot_surface`；`new_figure` 回傳
  `(Figure, Axes)`。範例 `08_visualization.py`。
- **0.6** `scw.manifold` 流形幾何：`TangentSpace`/`CotangentSpace`（`VectorSpace`
  子類，帶 `manifold`+`point`，不同點互不相容）、`Metric`（SPD 驗證、
  `inner`/`norm`、`flat`/`sharp` 音樂同構）、`Manifold` ABC +
  `EuclideanSpace(n)`（單位 metric）+ `Sphere(radius)`（球面座標，標準 metric，
  兩極排除）。範例 `09_manifolds.py`。
- **0.7** `scw.physics` 牛頓力學：`Particle`；力模型 `ConstantForce` /
  `SpringForce` / `CentralGravity` / `Drag`（前三者為 `ConservativeForce` 子類，
  附 `potential_energy` 且滿足 `F = -grad U`）；`System`（動量、動能、位能、
  總能量，非保守力求位能丟 `NumericalError`）；`simulate` / `Trajectory`
  （委派 `scw.numerical.solve_ivp` 積分 `dx/dt=v`、`dv/dt=F/m`）。範例
  `10_physics_simulation.py`。
- **0.8** `scw.experiments` 實驗追蹤與可重現性：`Experiment`（名稱 + 種子 +
  設定，`run` 回傳 `RunRecord`，`rng(label)` 給可重現生成器，`sweep` 掃描）；
  `RunRecord`/`Artifact`（不可變、可 JSON round-trip、含環境指紋與耗時）；
  `ResultStore`（JSON 紀錄目錄 + `index.json`，原子寫入，`query`/`best`/`summary`）；
  `Dataset`（可重現具名欄位 + `spec`，`split`/`fingerprint`/`from_spec`）。新例外
  `ExperimentError`（`ValueError`）。CLI 加 `scw experiments summary|list|show|best`。
  範例 `11_experiments.py`。

### 實驗層慣例（0.8 起）

- `scw/experiments/` 只依賴 `math_core` 與 `scw.exceptions`；**只有**
  `store.py` 碰檔案系統，其餘模組不得 import 檔案系統/CLI/繪圖。本層**計入**
  coverage（不像繪圖/symbolic 列入 omit），核心覆蓋率 ≥90%。
- **可重現性是可檢驗的性質**：`derive_seed(seed, label)` 由 SHA-256 決定子種子；
  `make_run_id` 由（實驗名、種子、設定、label）的 canonical JSON 決定，故「同設定
  同種子」必得同 id 與同數值。性質測試就釘這些（重跑一致、`Dataset` 由 spec 重建、
  store round-trip、split 恰好分割所有列）。
- `RunRecord.config`/`results`/`environment` 用 `MappingProxyType` 唯讀；
  `Dataset.columns` 防禦性複製（`np.array(..., copy=True)`）並回唯讀視圖——
  回歸測試會釘住「改外部陣列不影響 dataset」。
- 結果/設定必須 JSON 可序列化（`jsonable` 處理 numpy 純量/陣列、`.data` 物件、
  `Path`、`datetime`、集合），否則丟 `ExperimentError`，不靜默字串化。
- store 寫入先寫 `.tmp` 再 `replace`（原子），避免中斷留下半截紀錄；查詢排序用
  `started_at`，跨 store 穩定。

### 數值層慣例（0.4 起）

- 演算法一律放 `scw/numerical/`，接受 `math_core` 的 `Matrix`/`Vector`，**不得**反向
  污染領域模型；每個公開函式先驗證型別/形狀再委派 SciPy，錯的一律丟 SCW 例外
  （不讓裸 `numpy.linalg.LinAlgError` 外洩）。
- 分解結果用 `@dataclass(frozen=True)` 的 Result 物件，並提供 `reconstruct()`，
  讓性質測試能用「重建原矩陣」當不變量（實測最壞誤差 ~9e-12，對 `atol=1e-6`
  有 ~1000× 餘裕）。
- ODE 失敗屬執行期條件，用 `ConvergenceError`（`RuntimeError`）；形狀/維度問題才用
  `DimensionError`/`ShapeError`（`ValueError`）。`ODESolution.t`/`.y` 回唯讀視圖。

### 繪圖層慣例（0.5 起）

- Matplotlib **只**能在 `scw/visualization/` 內 import（集中在 `_backend.py` 的守衛
  import）；領域層與數值層不得 import 繪圖，公開數學方法不得回傳 figure。
- 每個繪圖函式回傳它畫上的 `Axes`（`new_figure`/`new_3d_figure` 回 `(Figure, Axes)`），
  接受既有 `ax=` 以便共用座標軸；驗證輸入後才丟 `TypeError`/`DimensionError`/
  `NumericalError`。
- 測試用 `pytest.importorskip("matplotlib")` + `matplotlib.use("Agg")`（headless），
  整檔在缺 extra 時跳過。繪圖程式碼列入 coverage omit（與 symbolic 一致）。
- 範例輸出寫進 gitignored 的 `scw_plots/`，勿把 PNG 提交進 repo。

### 物理層慣例（0.7 起）

- `scw/physics/` 只依賴 `math_core` 與 `numerical`；**不得** import CLI/繪圖/
  檔案系統。積分一律委派 `scw.numerical.solve_ivp`，物理層只組/拆狀態向量
  （`[positions..., velocities...]`）與提供力的模型。
- `Force` 是 ABC；保守力繼承 `ConservativeForce` 並提供 `potential_energy`，
  使「能量守恆」成為**可檢驗的性質**（性質測試以中央差分驗證 `F = -grad U`）。
  非保守力（`Drag`）不得謊報位能；`System.potential_energy` 遇非保守力丟
  `NumericalError`。
- 驗證先行：非正/非有限質量、負勁度、維度不一致、重複名稱、空系統一律明確失敗
  （`ValueError`/`DimensionError`/`NonFiniteError`）。重力在中心奇異點丟
  `ZeroDivisionError`，不可回傳 inf/nan 汙染積分器。
- `Trajectory` 的 `t`/`y` 回唯讀視圖；`positions`/`velocities`/`momentum` 等回
  `(n_points, dimension)` 形狀的 ndarray。
- 物理層**計入** coverage（不像繪圖/symbolic 列入 omit），核心覆蓋率 ≥90%。

## 文件語言

- **`README.md` 與 `docs/index.md` 以中文撰寫**，作為專案入口：整合**計畫**
  （連規格 `docs/spec/`）、**進度**（逐版狀態表，連各版 release）、**成果**
  （範例／notebook／gallery／離線指南），並含安裝／使用／解除安裝。
- 其餘文件（`docs/api.md`、`docs/development.md` 等）與程式碼註解維持英文；
  中文長篇說明集中在 `docs/offline.md` 與 README。
- 更新進度時：先改 `CHANGELOG.md`，再執行
  `uv run python scripts/sync_progress.py` 重生成 README 的版本狀態表
  （表格夾在 `<!-- progress:start -->` / `<!-- progress:end -->` 之間，**勿手改**；
  CI 與 pre-commit 會用 `--check` 擋下忘記同步的提交）。
  表格由規格 §11（版本與里程碑措辭）+ `CHANGELOG.md`（有日期段者視為已發行）
  產生；已發行版的中文一句說明在 `scripts/sync_progress.py` 的 `MILESTONES`。

## 發行說明（每個版本都要附中文指南）

每次發行（推 `v*` tag）時，release notes 必須包含同一份中文「安裝／欣賞／
操作／解除安裝」指南。**不要手寫貼上**，改用產生器以維持單一來源：

```bash
uv run python scripts/make_release_notes.py v0.7.0 -o notes.md   # 或設 GITHUB_REF_NAME
gh release create v0.7.0 --notes-file notes.md
```

- 英文「本次變更」取自 `CHANGELOG.md` 的 `## [x.y.z]` 段（單一來源）。
- 中文指南取自 `docs/offline.md`（單一來源；產生器會把版本字串換成目標版）。
- 「本版新增作品」由 git 歷史自動列出該版新增的 `examples/`、`notebooks/`。
- 新作品的中文一句說明加在 `scripts/make_release_notes.py` 的
  `WORK_DESCRIPTIONS`；漏加會退回顯示檔名。
- `.github/workflows/release.yml` 已接上產生器：推 tag 會自動產生並帶入中文指南
  （舊 tag 沒對應 CHANGELOG 段時，退回 GitHub 自動產生的 notes）。

## 已知環境注意事項

- 沙盒內建 `GITHUB_TOKEN`（`ghu_`）與 `GITHUB_PERSONAL_ACCESS_TOKEN`（`github_pat_`）
  皆為 **fine-grained**；建立 repo 需具備對應權限（見 test-repo 的 AGENTS.md 記載）。
- **改 repo 可見性（private↔public）需要 `administration=write`**，沙盒的 fine-grained
  token 未具備此 scope：`gh repo edit --visibility public` 與
  `PATCH /repos/{owner}/{repo}` 皆回 `403 Resource not accessible`。
  解法只能由使用者在 GitHub 網頁（Settings → General → Danger Zone →
  Change visibility）手動切換，或換一支具 `administration:write` 的 token。
- 沙盒 LLM proxy 可能對 `/chat/completions` 回 403；本專案 Phase 1 不需要 LLM。
