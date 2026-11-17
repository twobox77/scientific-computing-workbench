# 交接文件（Handover）

> 本文件是專案的**狀態快照與交接說明**，供下一位維護者（人或 AI agent）快速接手。
> 專案的**慣例與知識**（依賴方向、品質閘門、測試教訓）在
> [`AGENTS.md`](https://github.com/twobox77/scientific-computing-workbench/blob/main/AGENTS.md)，
> 本文件不重複，只做「現況 + 待辦 + 操作手冊」。
> 最後更新：2026-11-17。

## 1. 一句話總結

SCW（Scientific Computing Workbench）已達到 **1.0**：公開 API 凍結、所有公開
命名空間為 **stable**、安裝與使用文件齊備、CI 與發佈流程自動化、文件站已上線。
本輪工作的主題是 **「1.0 收尾」**：把 `provisional` 升為 `stable`、補齊
安裝／使用文件、接上 CI 發佈管線、補發缺漏的版本 tag 與 GitHub Release、
發佈文件站、設定 repo metadata。

## 2. 目前狀態

| 項目 | 狀態 |
|---|---|
| 版本 | **1.0.0**（`pyproject.toml` 與 `src/scw/__init__.py` 一致） |
| 分支 | `main`（直接 commit，不開 PR），與 `origin/main` 同步 |
| 最新 commit | `f5100bb` — docs(changelog): note the GitHub Pages documentation site |
| Git tags | `v0.1.0` … `v1.0.0`（連續無缺口） |
| GitHub Releases | `v0.1.0` … `v1.0.0` 全部存在，各含 wheel + sdist |
| 文件站 | <https://twobox77.github.io/scientific-computing-workbench/>（GitHub Pages，已上線） |
| repo metadata | description ✅、homepage ✅、topics ✅（`numpy`、`python`、`scientific-computing`） |
| 測試 | **495 passed**，核心覆蓋率 **97%** |
| 品質閘門 | ruff、complexity guard、format、mypy、public-API freeze、sync-progress、mkdocs `--strict` 全過 |
| CI | `CI`、`Docs`、`Release` 三條 workflow 皆綠 |

## 3. 本輪交付內容

- **公開 API 升為 stable**：`scripts/public_api.py` 新增 `STABILITY` 對照表（單一
  來源），`docs/public-api-frozen.json`（85 個名稱 / 10 個命名空間）逐命名空間標
  級並全部為 `stable`；`--check` 同時擋下「名稱增減」與「穩定性升降」。
- **文件**：新增 `docs/installation.md`（uv / pip / 原始碼、`all` extra、驗證、
  解除安裝）與 `docs/usage.md`（逐層任務導向導覽）。
- **打包與安裝驗證**：新增 `all` extra；`scripts/verify_install.sh` 建 wheel →
  乾淨 venv → 匯入所有公開命名空間；CI 獨立 `install` job 實跑。
- **發佈流程**：`release.yml` 加 tag↔版本一致性守門；推 `v*` 自動建 Release
  並上傳 wheel/sdist，notes 由 `scripts/make_release_notes.py` 產生（英文 CHANGELOG
  + 中文離線指南 + 本版新增作品）。
- **文件站**：新增 `.github/workflows/docs.yml`（`mkdocs build --strict` +
  `actions/deploy-pages`）；`mkdocs.yml` 加 `site_url`/`repo_url`。
- **補發版本**：`v0.8.0`（experiments）、`v0.9.0`（API freeze）、`v1.0.0`（1.0 收尾）。

## 4. 系統怎麼跑（操作手冊）

### 4.1 接手步驟

```bash
# 首次取得
git clone https://github.com/twobox77/scientific-computing-workbench.git
cd scientific-computing-workbench

# 之後更新：一律 git pull，不要重新 clone（見 AGENTS.md）
git pull

# 安裝全部依賴（含 optional 與 dev）
uv sync --all-extras
```

### 4.2 品質閘門（每個提交都要過）

```bash
uv run ruff check .
uv run python scripts/complexity_guard.py
uv run ruff format --check .
uv run mypy src/scw
uv run pytest --cov=scw --cov-report=term-missing
```

另有兩個「產生檔同步」檢查，忘記同步會讓 CI 紅：

```bash
uv run python scripts/sync_progress.py --check   # README 進度表
uv run python scripts/public_api.py --check      # 公開 API 快照
```

### 4.3 驗收重跑

```bash
bash scripts/verify_phase1.sh      # Phase 1 全部驗收（見 docs/phase1-acceptance.md）
bash scripts/verify_install.sh symbolic visualization   # 打包/安裝煙霧測試
```

### 4.4 發佈一個新版本（SOP）

```bash
# 1) 改版本（三處一起）
#    pyproject.toml / src/scw/__init__.py / uv.lock
# 2) 寫 CHANGELOG.md 的 ## [x.y.z] 段
# 3) 同步 README 進度表
uv run python scripts/sync_progress.py
# 4) 產生中文 release notes（可先本機檢查）
uv run python scripts/make_release_notes.py vX.Y.Z -o notes.md
# 5) 打 tag 並推（release.yml 會自動建 Release 並上傳 wheel/sdist）
git tag -a vX.Y.Z -m "SCW X.Y.Z — <一句話>"
git push origin vX.Y.Z
```

> `release.yml` 會先檢查 tag 與 `pyproject.toml`／`__version__` 一致，不一致就失敗。

### 4.5 文件站

- 站台：<https://twobox77.github.io/scientific-computing-workbench/>
- `main` 動到 `docs/`、`mkdocs.yml`、`README.md` 或 `docs.yml` 時自動重建並發佈。
- 本機預覽：`uv run mkdocs serve -a 127.0.0.1:8000`。
- Pages 已在 repo 設定啟用（Source = GitHub Actions）。

## 5. 環境限制與憑證（重要）

- 沙盒內建兩支 **fine-grained** token：`GITHUB_TOKEN`（`ghu_`）與
  `GITHUB_PERSONAL_ACCESS_TOKEN`（`github_pat_`）。
- **可以**：push、建 tag、建/編輯 GitHub Release、讀取 Actions、建立 repo。
- **不行（皆回 403）**：需要 `administration:write` 的操作——
  - 改 repo 可見性（private↔public）
  - 改 description / homepage / **topics**
  - **建立 GitHub Pages site**（`actions/configure-pages` 帶 `enablement: true`
    也不行；workflow 的 `GITHUB_TOKEN` 同樣 403）
  以上只能由**使用者在 GitHub 網頁**操作，或改用一支具該 scope 的 token。
- 目前 `docs.yml` 已把 deploy 設計成「以 Pages 是否啟用為閘」，未啟用時只跳過、
  build 永遠綠燈；因此就算換到未啟用 Pages 的環境也不會紅燈。
- 沙盒 LLM proxy 可能對 `/chat/completions` 回 403；本專案不需要 LLM。

## 6. 待辦 / 建議下一步

優先序由高到低（皆非阻斷性）：

1. **topics 可再補齊**（可選）：目前只有 3 個，建議再加
   `scipy`、`linear-algebra`、`differential-geometry`、`physics`、
   `symbolic-math`、`numerical-methods`、`visualization`。需在網頁操作。
2. **發佈到 PyPI**（可選）：目前只發到 GitHub Releases；若要做
   `pip install scw`，需在 PyPI 註冊專案 + Trusted Publishing，再加 `publish.yml`。
   （PyPI 端設定需使用者本人。）
3. **覆蓋率推上 100%**（低風險）：現為 97%，未涵蓋集中在
   `physics/forces.py`（7 行）、`physics/simulation.py`（2 行）、
   `physics/system.py`（1 行）等防禦分支。
4. **效能回歸護欄**（中）：`benchmarks/` 目前只是本機微基準，可考慮納入 CI 門檻。
5. **1.1 功能**（需先定範圍）：規格 §1.2 把 Tensor Calculus / PDE 列為
   「1.0 不做」，可作為 1.1 主題；或加新的數學層、CLI 子命令、更多 notebook。

## 7. 檔案地圖（接手時最常碰的）

```text
src/scw/
  math_core/      Vector/Covector/Matrix/LinearMap/Tensor/Basis、VectorSpace
  numerical/      SciPy adapter：lstsq、lu/qr/svd/cholesky/eigh、solve_ivp
  symbolic/       SymPy adapter（optional extra）
  visualization/  Matplotlib adapter（optional extra）
  manifold/       TangentSpace/CotangentSpace、Metric、Manifold/EuclideanSpace/Sphere
  physics/        Particle、Force 家族、System、simulate/Trajectory
  experiments/    Experiment、run records、Dataset、store
  cli/            Typer 入口（scw）
scripts/
  public_api.py            公開 API 快照與穩定性（--check）
  sync_progress.py         README 進度表產生器（--check）
  make_release_notes.py    Release notes 產生器
  complexity_guard.py      AST 靜態迴圈護欄
  verify_install.sh        wheel 安裝煙霧測試
  verify_phase1.sh         Phase 1 驗收重跑
.github/workflows/         ci.yml / docs.yml / release.yml
docs/                      文件站來源（見 mkdocs.yml 的 nav）
docs/public-api-frozen.json 公開 API 凍結快照（勿手改，用 scripts 重生）
```

## 8. 已知的地雷（避免重蹈覆轍）

- **更新既有工作區一律 `git pull`**，不要重新 `git clone`（會多出同名資料夾）。
- **`uv sync --extra <x>` 會移除其他 extra 與 dev 依賴**；要保留全套用
  `uv sync --all-extras`。
- **`ruff check .` 會 lint `.ipynb`**：notebook 必須 lint 乾淨，import 集中在
  第一個 cell、移除未用 import、不寫分號。
- **`.pre-commit-config.yaml` 的 ruff rev 必須與 `uv.lock` 的 ruff 版本一致**，
  否則乾淨樹上會冒假失敗。
- **性質測試的浮點容差要隨尺度設定**（定律類用 `rtol=1e-9, atol=1e-6`，運算元
  壓到 `|x|<=1e3`），別用 `np.allclose` 預設值，否則本機過、CI 掛。
- 更完整的測試教訓見 `AGENTS.md` 的「測試教訓」與「開發慣例」。
