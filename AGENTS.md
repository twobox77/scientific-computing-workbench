# AGENTS.md

本檔給 AI agent 讀取，用來保存此倉庫的慣例與知識，讓不同對話之間保持一致。

## 倉庫定位

- 名稱：`twobox77/scientific-computing-workbench`（SCW，Scientific Computing Workbench）。
- 用途：以 Python 為核心的**個人科學計算工作台**。自行定義數學語意與型別
  （Vector / Covector / Matrix / LinearMap），底層數值運算交給 NumPy / SciPy。
- 架構：**模組化單體（modular monolith）**，單一 repository，`src/` layout。
- 介面：Python API、CLI（Typer）、Jupyter。
- 授權：MIT。預設分支：`main`。
- 規格來源：`docs/spec/SCW_1.0_Technical_Specification_and_Phase1_Plan.md`。

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
- `src/scw/numerical/` — 數值演算法（SciPy adapter）。
- `src/scw/symbolic/`、`visualization/`、`physics/`、`experiments/` — Phase 1 僅建立套件邊界。
- `src/scw/cli/` — 命令列入口（只解析參數、呼叫公開 API，不含數學演算法）。
- `tests/{unit,property,integration,regression}/` — 單元、性質（Hypothesis）、整合、回歸測試。
- `docs/` — MkDocs Material 文件；`docs/spec/` 放規格正本。

## 品質閘門（每個 PR 必過）

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/scw
uv run pytest --cov=scw --cov-report=term-missing
```

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
- 版本：Semantic Versioning；1.0 前用 `0.y.z`，破壞性變更記錄於 `CHANGELOG.md`。
- 直接 commit 進 `main`（不開 PR），除非另有指示。
- 公開 API 集中由 `__init__.py` 匯出；內部模組路徑在 1.0 前可調整。

## 路線圖（規格 §11）

0.2 Tensor → 0.3 Symbolic → 0.4 Numerical/ODE → 0.5 Visualization →
0.6 Manifold → 0.7 Physics → 0.8 Experiments → 0.9 API 穩定化 → 1.0 穩定。
版本以驗收條件與模組成熟度決定，不按日曆。

## 已知環境注意事項

- 沙盒內建 `GITHUB_TOKEN`（`ghu_`）與 `GITHUB_PERSONAL_ACCESS_TOKEN`（`github_pat_`）
  皆為 **fine-grained**；建立 repo 需具備對應權限（見 test-repo 的 AGENTS.md 記載）。
- 沙盒 LLM proxy 可能對 `/chat/completions` 回 403；本專案 Phase 1 不需要 LLM。
