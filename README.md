# DEP CM Factor Simulator

## English

DEP CM Factor Simulator is a Python GUI application for visualizing the relationship between frequency and the real part of the Clausius-Mossotti factor, `Re[K]`, in dielectrophoresis (DEP).

This application is intended to support master's research on DEP responses of cells and microparticles. It allows users to compare frequency-dependent behavior by changing physical and electrical parameters.

## 日本語

DEP CM Factor Simulator は、誘電泳動（DEP: Dielectrophoresis）における Clausius-Mossotti 因子の実部 `Re[K]` と周波数の関係を可視化するための Python GUI アプリケーションです。

修士研究における細胞・微粒子の DEP 応答確認を目的として、パラメータを変更しながら周波数依存性を比較できるようにしています。

---

# Features / 機能

## English

- Calculate the real part of the CM factor, `Re[K]`
- Plot `Re[K]` against frequency `f [Hz]`
- Provide a GUI for parameter input
- Provide a GUI for graph visualization
- Overlay multiple simulation results on the same graph
- Open simulation results in a new graph window
- Clear the displayed graph
- Save graphs as PNG files
- Show error messages for invalid input values
- Manage the Python environment and dependencies using `uv`
- Reproduce the frequency dependence of the CM factor shown in reference paper Figure 1(a)–(h)
- Save and load parameter conditions as CSV files
- Add custom graph labels for each experimental condition

## 日本語

- CM因子の実部 `Re[K]` を計算
- 周波数 `f [Hz]` に対する `Re[K]` をグラフ表示
- パラメータ入力用GUI
- グラフ表示用GUI
- 複数条件の重ね描き
- 新しいWindowでのグラフ表示
- グラフクリア
- PNG保存
- 不正な入力値に対するエラー表示
- `uv` による環境構築・依存関係管理
- 参考論文 Figure 1(a)〜(h) に対応するCM因子の周波数依存性の再現
- パラメータ条件のCSV保存・読み込み
- 実験条件ごとの任意グラフラベル入力

---

# Requirements / 必要環境

## English

- macOS
- Python 3.12
- uv

## 日本語

- macOS
- Python 3.12
- uv

---

# Setup / セットアップ

## English

Install dependencies with `uv`.

    uv sync

## 日本語

`uv` を用いて依存関係を同期します。

    uv sync

---

# Run / 実行方法

## English

Start the GUI application.

    uv run dep-cm-sim

## 日本語

GUIアプリケーションは以下で起動できます。

    uv run dep-cm-sim

---

# Usage / 使い方

## English

1. Start the application.
2. Enter values in the parameter input window.
3. Click `現在のグラフに重ねる` to plot the result on the current graph window.
4. The graph window shows the relationship between `Re[K]` and frequency.
5. Change parameters and click `現在のグラフに重ねる` again to overlay another curve.
6. Click `新しいWindowで表示` to open the result in a new graph window.
7. Click `PNG保存` in the graph window to save the graph as a PNG file.
8. Click `グラフをクリア` to remove the displayed curves.
9. Enter a custom graph label in the `グラフラベル` field if needed.
10. If the graph label is empty, the application automatically uses `sigma_s=... S/m` as the legend label.
11. Click `CSV保存` to save the current parameter condition as a CSV file.
12. Click `CSV読み込み` to restore a saved parameter condition from a CSV file.

## 日本語

1. アプリを起動する
2. パラメータ入力画面で値を入力する
3. 「現在のグラフに重ねる」を押す
4. グラフWindowに `Re[K]` と周波数の関係が表示される
5. 条件を変更して再度「現在のグラフに重ねる」を押すと、同じグラフ上に曲線が追加される
6. 「新しいWindowで表示」を押すと、別Windowにグラフが表示される
7. グラフWindowの「PNG保存」で画像を保存できる
8. 「グラフをクリア」で表示中の曲線を削除できる
9. 必要に応じて「グラフラベル」に実験条件名を入力する
10. 「グラフラベル」が空欄の場合は、従来通り `sigma_s=... S/m` が凡例に表示される
11. 「CSV保存」で現在のパラメータ条件をCSVファイルとして保存できる
12. 「CSV読み込み」で保存済みのCSVからパラメータ条件を復元できる

---

# Parameters / パラメータ

| Parameter | Symbol | Unit | Default | Description |
|---|---:|---:|---:|---|
| Graph label / グラフラベル | `label` | - | empty | Custom legend label. If empty, `sigma_s=... S/m` is used automatically. |
| Membrane capacitance / 細胞膜容量 | `C_m` | F/m^2 | 0.015 | Cell membrane capacitance |
| Cell radius / 細胞半径 | `r` | m | 6.7e-6 | Cell radius |
| Cytoplasm relative permittivity / 細胞質の比誘電率 | `epsilon_c / epsilon_0` | - | 60 | Relative permittivity of cytoplasm |
| Solution relative permittivity / 溶液の比誘電率 | `epsilon_s / epsilon_0` | - | 80 | Relative permittivity of solution |
| Cytoplasm conductivity / 細胞質導電率 | `sigma_c` | S/m | 0.5 | Conductivity of cytoplasm |
| Solution conductivity / 溶液導電率 | `sigma_s` | S/m | 2.0e-4 | Conductivity of solution |
| Minimum frequency / 最小周波数 | `f_min` | Hz | 1 | Lower bound of frequency |
| Maximum frequency / 最大周波数 | `f_max` | Hz | 1.0e10 | Upper bound of frequency |
| Number of points / 計算点数 | `N` | points | 1000 | Number of log-spaced frequency points |

---

# CSV Save and Load / CSV保存・読み込み

## English

The application can save the current parameter condition as a CSV file and load it later.

The saved CSV includes both numerical parameters and the custom graph label:

    graph_label
    membrane_capacitance
    radius_m
    eps_c_relative
    eps_s_relative
    sigma_c
    sigma_s
    f_min
    f_max
    num_points

If `graph_label` is empty, the graph legend is automatically generated from `sigma_s`.

Example:

    sigma_s=2.00e-04 S/m

If `graph_label` is provided, the entered label is used directly in the graph legend.

Example:

    HL60_default

## 日本語

本アプリケーションでは、現在のパラメータ条件をCSVファイルとして保存し、後から読み込むことができます。

保存されるCSVには、数値パラメータに加えて、任意のグラフラベルも含まれます。

    graph_label
    membrane_capacitance
    radius_m
    eps_c_relative
    eps_s_relative
    sigma_c
    sigma_s
    f_min
    f_max
    num_points

`graph_label` が空欄の場合は、従来通り `sigma_s` から凡例が自動生成されます。

例:

    sigma_s=2.00e-04 S/m

`graph_label` が入力されている場合は、その文字列がグラフ凡例にそのまま使用されます。

例:

    HL60_default


---

# Model / 計算モデル

## English

The application calculates the real part of the Clausius-Mossotti factor, `Re[K]`, using the frequency-dependent model implemented in `src/dep_cm_sim/equations.py`.

The angular frequency is defined as:

    omega = 2 pi f

The time constants are defined as:

    tau_ms = C_m r / sigma_s
    tau_mc = C_m r / sigma_c
    tau_s = epsilon_s / sigma_s
    tau_c = epsilon_c / sigma_c

The permittivities are calculated as:

    epsilon_s = epsilon_s_relative * epsilon_0
    epsilon_c = epsilon_c_relative * epsilon_0

The application plots the real part of the CM factor:

    Re[K]

## 日本語

本アプリケーションでは、`src/dep_cm_sim/equations.py` に実装された周波数依存モデルを用いて、Clausius-Mossotti 因子の実部 `Re[K]` を計算します。

角周波数は以下で定義します。

    omega = 2 pi f

各時定数は以下で定義します。

    tau_ms = C_m r / sigma_s
    tau_mc = C_m r / sigma_c
    tau_s = epsilon_s / sigma_s
    tau_c = epsilon_c / sigma_c

誘電率は以下で計算します。

    epsilon_s = epsilon_s_relative * epsilon_0
    epsilon_c = epsilon_c_relative * epsilon_0

本アプリケーションでは、CM因子の実部をグラフ化します。

    Re[K]

---

# Reproducing Reference Paper Figure 1(a)–(h) / 参考論文 Figure 1(a)〜(h) の再現

## English

The script `src/dep_cm_sim/reproduce_paper_figure.py` reproduces the frequency dependence of the real part of the CM factor for the solution conductivity conditions corresponding to Figure 1(a)–(h) in the reference paper.

The following solution conductivity values are used:

| Label | Solution conductivity `sigma_s` |
|---|---:|
| (a) | 2.0e-4 S/m |
| (b) | 1.0e-3 S/m |
| (c) | 1.0e-2 S/m |
| (d) | 1.0e-1 S/m |
| (e) | 2.0e-1 S/m |
| (f) | 4.0e-1 S/m |
| (g) | 5.0e-1 S/m |
| (h) | 1.0e0 S/m |

Run the script with:

    PYTHONPATH=src uv run python src/dep_cm_sim/reproduce_paper_figure.py

The output image is saved as:

    outputs/paper_figure_reproduction.png

## 日本語

`src/dep_cm_sim/reproduce_paper_figure.py` は、参考論文 Figure 1(a)〜(h) に対応する溶液導電率条件について、CM因子の実部の周波数依存性を一括で再現するためのスクリプトです。

使用している溶液導電率は以下です。

| Label | 溶液導電率 `sigma_s` |
|---|---:|
| (a) | 2.0e-4 S/m |
| (b) | 1.0e-3 S/m |
| (c) | 1.0e-2 S/m |
| (d) | 1.0e-1 S/m |
| (e) | 2.0e-1 S/m |
| (f) | 4.0e-1 S/m |
| (g) | 5.0e-1 S/m |
| (h) | 1.0e0 S/m |

以下のコマンドで実行できます。

    PYTHONPATH=src uv run python src/dep_cm_sim/reproduce_paper_figure.py

出力画像は以下に保存されます。

    outputs/paper_figure_reproduction.png

---

# Development / 開発

## English

Run lint:

    uv run ruff check .

Run tests:

    uv run pytest

Run the demo plot script:

    PYTHONPATH=src uv run python src/dep_cm_sim/demo_plot.py

## 日本語

lintを実行します。

    uv run ruff check .

テストを実行します。

    uv run pytest

デモ用グラフスクリプトを実行します。

    PYTHONPATH=src uv run python src/dep_cm_sim/demo_plot.py

---

# Project Structure / プロジェクト構成

    dep-cm-factor-simulator/
    - src/dep_cm_sim/equations.py
    - src/dep_cm_sim/plotter.py
    - src/dep_cm_sim/demo_plot.py
    - src/dep_cm_sim/reproduce_paper_figure.py
    - src/dep_cm_sim/parameter_io.py
    - src/dep_cm_sim/gui/parameter_window.py
    - src/dep_cm_sim/gui/graph_window.py
    - tests/test_equations.py
    - tests/test_parameter_io.py
    - pyproject.toml
    - uv.lock
    - README.md

---

# Notes / 注意事項

## English

This software is intended for research support and parameter comparison.

Before using simulation results for formal academic conclusions, confirm the model assumptions, parameter units, and equation definitions with the original literature and a specialist.

## 日本語

本ソフトウェアは、研究補助およびパラメータ比較を目的としたものです。

シミュレーション結果を正式な学術的結論に用いる前に、モデルの仮定、パラメータ単位、式の定義を原著論文および専門家に確認することを推奨します。