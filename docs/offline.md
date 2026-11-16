# 離線欣賞與操作

本頁說明如何在**沒有網路**的環境中「看」與「玩」SCW。發行版（GitHub Releases）
的說明也附有同樣內容。

## 0. 取得原始碼並進入專案目錄

`uv` 必須在**有 `pyproject.toml` 的目錄**執行。先確認你是否已經有原始碼：

```bash
ls pyproject.toml        # 有列出檔案 → 你已經在專案目錄內，直接跳到「0.5 安裝依賴」
```

若還沒取得，選下面任一種。**三種來源的前置條件不同**，請照各自的說明做：

**A. 用 git 取得**（需要網路 + 對本 repo 的存取權；本 repo 為 private）

```bash
git clone https://github.com/twobox77/scientific-computing-workbench.git
cd scientific-computing-workbench        # ← 一定要進來，這裡才有 pyproject.toml
```

- private repo，需要 GitHub 帳號權限；未設定好會要你輸入帳密或 Personal Access Token。
- 若目錄 `scientific-computing-workbench/` **已存在**（例如之前 clone 過），
  **不要再跑 `git clone`**，直接 `cd` 進去就好：

```bash
cd scientific-computing-workbench
git pull                                 # 想更新到最新時
```

**B. 用 Release 的原始碼壓縮包**（必須先下載檔案到**當前目錄**）

先從本頁下方 Assets 下載 `scw-0.6.0.tar.gz` 到當前目錄，再：

```bash
ls scw-0.6.0.tar.gz                      # 確認檔案在，否則下一步會「無法 open」
tar xzf scw-0.6.0.tar.gz                 # 解開後目錄名為 scw-0.6.0/
cd scw-0.6.0                             # ← 一定要進來
```

**C. 只安裝套件**（必須先下載 `.whl`；不跑範例／文件／notebook）

```bash
uv pip install scw-0.6.0-py3-none-any.whl   # 或 uv pip install scw-0.6.0.tar.gz
```

> 只有 A、B 兩種（原始碼）能跑範例、文件站與 notebook；C 只裝套件。

## 0.5 安裝依賴（一次性）

在**上一步 `cd` 進去的專案目錄內**，連網時：

```bash
uv sync --all-extras --frozen      # 安裝全部依賴（含繪圖 / notebook / 互動）
```

完全離線時，先在可連網的機器執行 `uv sync --all-extras`，取得 uv 快取
（`uv cache dir`），再把整個 `.venv/`（或 uv 快取）複製到離線機器。
離線機器上之後的指令都要在**同一個專案目錄**內執行。

### 常見錯誤

- `No pyproject.toml found in current directory or any parent directory`
  → 你**不在專案目錄內**（例如還停在 `~`）。先 `cd` 進去再重跑：

  ```bash
  cd scientific-computing-workbench   # 或 cd scw-0.6.0（依你的來源）
  uv sync --all-extras --frozen
  ```

- `fatal: destination path 'scientific-computing-workbench' already exists and is not an empty directory`
  （中文：目的地路徑已存在，並且不是一個空目錄）
  → 目錄已存在，**不必再 clone**。直接 `cd scientific-computing-workbench`；
  要更新就 `git pull`。想重新 clone 請先把舊目錄改名或刪除。

- `tar (child): scw-0.6.0.tar.gz: Cannot open: No such file or directory`
  （中文：無法 open：沒有此一檔案或目錄）
  → 你還沒把壓縮包**下載到當前目錄**。先從 Release Assets 下載，或改用 git（A）。

## 1. 純文字：跑範例、看數值

```bash
uv run python examples/09_manifolds.py        # 0.6 流形：切空間、metric、flat/sharp
uv run python examples/08_visualization.py    # 繪圖範例，輸出 PNG 到 scw_plots/
uv run python examples/06_decompositions.py   # 0.4 分解：LU / QR / SVD / Cholesky / eigh
```

## 2. 看文件網站（離線）

```bash
uv run mkdocs serve -a 127.0.0.1:8000     # 瀏覽器開 http://127.0.0.1:8000
```

只想產生靜態站（可直接用瀏覽器開檔）：

```bash
uv run mkdocs build --strict              # 產出 site/，開 site/index.html
```

重點頁面：**Gallery**、Mathematics → Manifolds / Visualization / Numerical methods。

## 3. 動手操作（Jupyter）

```bash
uv run jupyter lab
```

- `notebooks/01_scw_quickstart.ipynb` — 基礎導覽。
- `notebooks/02_manifolds.ipynb` — 0.6 靜態教學（已內嵌圖，讀即可）。
- `notebooks/03_manifolds_interactive.ipynb` — 3D 圖**可拖曳旋轉**，附滑桿
  （需 `interactive` extra）。

互動版操作：3D 圖上**左鍵拖曳可旋轉、滾輪縮放、右鍵拖曳可平移**；拖動
`theta` / `phi` 滑桿可即時移動球面上的點，標題顯示 `|e_theta|`、`|e_phi|`，
可觀察 `|e_phi| = r sinθ` 在赤道最大、越靠兩極越小。

## 4. 離線欣賞圖片（不開 notebook）

```bash
uv sync --extra visualization
uv run python scripts/build_gallery.py     # 產生 docs/assets/gallery/*.png
```

再用系統的圖片檢視器開啟 `docs/assets/gallery/` 內的 PNG。
