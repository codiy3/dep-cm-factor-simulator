# DEP CM Factor Simulator

## English

DEP CM Factor Simulator is a Python GUI application for visualizing the frequency dependence of the real part of the Clausius-Mossotti factor, `Re[K]`, in dielectrophoresis (DEP).

The application is designed for educational, simulation, and parameter-comparison purposes. Users can change physical and electrical parameters, compare multiple conditions, save graphs, and reproduce a reference DEP spectrum from the literature.

## 日本語

DEP CM Factor Simulator は、誘電泳動（DEP: Dielectrophoresis）における Clausius-Mossotti 因子の実部 `Re[K]` と周波数の関係を可視化するための Python GUI アプリケーションです。

教育用途、シミュレーション、パラメータ比較を目的としており、物理・電気的パラメータを変更しながら複数条件の比較、グラフ保存、参考文献に掲載されたDEPスペクトルの再現を行うことができます。

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
- Reproduce the frequency dependence of the CM factor shown in reference Figure 1(a)–(h)
- Run the reference Figure 1(a)–(h) reproduction directly from the GUI
- Save and load parameter conditions as CSV files
- Add custom graph labels for each simulation condition

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
- 参考文献 Figure 1(a)〜(h) に対応するCM因子の周波数依存性の再現
- GUIから参考文献 Figure 1(a)〜(h) の再現グラフを直接生成
- パラメータ条件のCSV保存・読み込み
- シミュレーション条件ごとの任意グラフラベル入力

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
13. Click `論文図(a)〜(h)を再現` to generate the reference Figure 1(a)–(h) reproduction graph directly from the GUI.

## 日本語

1. アプリを起動する
2. パラメータ入力画面で値を入力する
3. 「現在のグラフに重ねる」を押す
4. グラフWindowに `Re[K]` と周波数の関係が表示される
5. 条件を変更して再度「現在のグラフに重ねる」を押すと、同じグラフ上に曲線が追加される
6. 「新しいWindowで表示」を押すと、別Windowにグラフが表示される
7. グラフWindowの「PNG保存」で画像を保存できる
8. 「グラフをクリア」で表示中の曲線を削除できる
9. 必要に応じて「グラフラベル」に条件名を入力する
10. 「グラフラベル」が空欄の場合は、従来通り `sigma_s=... S/m` が凡例に表示される
11. 「CSV保存」で現在のパラメータ条件をCSVファイルとして保存できる
12. 「CSV読み込み」で保存済みのCSVからパラメータ条件を復元できる
13. 「論文図(a)〜(h)を再現」を押すと、参考文献 Figure 1(a)〜(h) に対応する8条件のグラフをGUIから直接生成できる

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

# Cell Parameter Templates / 細胞パラメータテンプレート

## English

The application provides cell parameter templates for parameters that are relatively cell-specific:

    membrane_capacitance
    radius_m
    eps_c_relative
    sigma_c

A default template, `reference_cell`, is available. Users can also save their own templates from the GUI.

User-defined templates are saved locally to:

    templates/user_cell_templates.json

This file is excluded from Git tracking so that local experimental or user-specific settings are not committed accidentally.

Cell templates do not include solution or simulation settings such as:

    sigma_s
    eps_s_relative
    f_min
    f_max
    num_points
    graph_label

These values are treated as experimental or plotting conditions rather than cell-specific properties.

## 日本語

本アプリケーションでは、細胞ごとに比較的一定になりやすい以下のパラメータを、細胞テンプレートとして管理できます。

    membrane_capacitance
    radius_m
    eps_c_relative
    sigma_c

デフォルトテンプレートとして `reference_cell` が用意されています。また、GUI上からユーザー自身のテンプレートを保存できます。

ユーザー定義テンプレートはローカルに以下のファイルとして保存されます。

    templates/user_cell_templates.json

このファイルはGit管理対象外にしているため、ローカルの実験条件やユーザー固有設定を誤ってコミットしにくくしています。

細胞テンプレートには、以下のような溶液条件・シミュレーション条件は含めません。

    sigma_s
    eps_s_relative
    f_min
    f_max
    num_points
    graph_label

これらは細胞固有値ではなく、実験条件または描画条件として扱います。


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

    condition_A

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

    condition_A

---

# Solution Conductivity Optimization / 最適溶液導電率探索

## English

This application can numerically search for the solution conductivity `sigma_s` that improves separation performance between two selected cell templates.

The optimization is designed for DEP-based cell separation. For each candidate `sigma_s`, the application calculates the real part of the Clausius-Mossotti factor, `Re[K]`, for two cells over a frequency range. The best condition is selected according to the selected optimization mode.

## Purpose

In dielectrophoresis, the sign and magnitude of `Re[K]` determine the direction and strength of the DEP response:

- `Re[K] > 0`: positive DEP, where cells are attracted toward stronger electric fields
- `Re[K] < 0`: negative DEP, where cells are repelled from stronger electric fields

Therefore, simply maximizing the numerical difference between two curves is not always sufficient for practical separation. For selective trapping or separation, it is often important to find a condition where one cell shows positive DEP and the other shows negative DEP.

## Input Parameters

The optimization uses the following inputs:

| Input | Meaning |
|---|---|
| Cell template 1 | First cell parameter template |
| Cell template 2 | Second cell parameter template |
| `eps_s_relative` | Relative permittivity of the solution |
| `sigma_s_min` | Lower bound of solution conductivity search range |
| `sigma_s_max` | Upper bound of solution conductivity search range |
| `num_sigma_points` | Number of logarithmically spaced `sigma_s` candidates |
| `f_min` | Lower bound of frequency range |
| `f_max` | Upper bound of frequency range |
| `num_frequency_points` | Number of logarithmically spaced frequency points |
| Optimization mode | `difference_only` or `opposite_sign` |

Cell-specific parameters are taken from the selected cell templates:

    membrane_capacitance
    radius_m
    eps_c_relative
    sigma_c

Solution and simulation parameters are taken from the GUI input fields.

## Numerical Search Design

The optimization is implemented as a logarithmic grid search over candidate solution conductivities.

Overall flow:

1. Generate candidate solution conductivities.

        sigma_s_candidates = logspace(log10(sigma_s_min), log10(sigma_s_max), num_sigma_points)

2. Generate frequency points.

        frequency_hz = logspace(log10(f_min), log10(f_max), num_frequency_points)

3. For each candidate `sigma_s`, calculate two `Re[K]` curves.

        Re[K]_1(f, sigma_s)
        Re[K]_2(f, sigma_s)

4. Evaluate the separation score according to the selected optimization mode.

5. Select the `sigma_s` and frequency `f_opt` that produce the best score.

Main implementation files:

    src/dep_cm_sim/condition_optimizer.py
    src/dep_cm_sim/gui/parameter_window.py
    src/dep_cm_sim/gui/graph_window.py

## Difference-only Mode

The `difference_only` mode searches for the condition where the absolute difference between two `Re[K]` curves is maximized.

For each candidate `sigma_s`, the application calculates:

    score(f, sigma_s) = |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

Then it finds the frequency where the score is largest:

    f_opt = argmax_f |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

Finally, it selects the `sigma_s` that gives the largest score over all candidates:

    sigma_s_opt = argmax_sigma_s max_f |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

This mode is useful when the goal is to find the maximum numerical separation between two CM factor curves.

However, this mode does not require the two DEP responses to have opposite signs. Therefore, both cells may still show positive DEP or both may show negative DEP at the optimum.

## Opposite-sign Mode

The `opposite_sign` mode searches only for conditions where the two cells show opposite DEP responses.

A frequency point is considered valid only when one of the following conditions is satisfied:

    Re[K]_1 > 0 and Re[K]_2 < 0

or

    Re[K]_1 < 0 and Re[K]_2 > 0

For valid frequency points, the application calculates:

    score(f, sigma_s) = |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

Then it selects the valid point with the largest score.

This mode is especially important for DEP separation because it directly searches for a condition where one cell is attracted toward stronger electric fields while the other cell is repelled from stronger electric fields.

If no opposite-sign condition is found within the search range, the application raises an error and the GUI shows an error dialog.

## Boundary Warning

If the optimal `sigma_s` is found at the lower or upper boundary of the search range, the GUI displays a warning.

This means the current search range may be too narrow. For example, if the optimum is found at `sigma_s_min`, a better condition may exist below the current lower bound.

In that case, users should consider expanding the search range, such as:

    sigma_s_min: 1.0e-5
    sigma_s_max: 1.0
    num_sigma_points: 50

## GUI Usage

In the parameter window, users can select:

- Cell template 1
- Cell template 2
- Minimum `sigma_s`
- Maximum `sigma_s`
- Number of `sigma_s` search points
- Optimization mode:
  - Difference-only / 差分最大
  - Opposite-sign / 符号分離

After pressing the optimization button, the application opens a graph window and displays:

- the two `Re[K]` curves at the optimized `sigma_s`
- the optimized frequency marker
- the optimization mode
- the values of `Re[K]_1` and `Re[K]_2` at the optimum

---

## 日本語

本アプリケーションでは、2つの細胞テンプレートを用いて、細胞間のDEP応答差が大きくなる溶液導電率 `sigma_s` を数値探索できます。

この機能は、DEPを用いた細胞分離・捕捉条件の設計を支援するためのものです。候補となる `sigma_s` を対数スケールで生成し、それぞれの `sigma_s` に対して、周波数範囲内の `Re[K]` 曲線を2細胞分計算します。その後、選択された最適化モードに従って、最も分離性能が高い条件を探索します。

## 目的

誘電泳動では、Clausius-Mossotti因子の実部 `Re[K]` の符号と大きさによって、細胞が受けるDEP力の向きと強さが変わります。

- `Re[K] > 0`: 正のDEP。細胞は電場の強い領域へ引き寄せられる
- `Re[K] < 0`: 負のDEP。細胞は電場の強い領域から遠ざかる

そのため、実際のDEP分離では、単に2曲線の差が大きいだけでは不十分な場合があります。特に、一方の細胞が正のDEP、もう一方の細胞が負のDEPを示す条件は、選択的な捕捉や分離において重要です。

## 入力パラメータ

最適化では以下の入力を使用します。

| 入力 | 意味 |
|---|---|
| 細胞テンプレート1 | 1つ目の細胞パラメータテンプレート |
| 細胞テンプレート2 | 2つ目の細胞パラメータテンプレート |
| `eps_s_relative` | 溶液の比誘電率 |
| `sigma_s_min` | 溶液導電率の探索下限 |
| `sigma_s_max` | 溶液導電率の探索上限 |
| `num_sigma_points` | `sigma_s` の探索点数 |
| `f_min` | 周波数範囲の下限 |
| `f_max` | 周波数範囲の上限 |
| `num_frequency_points` | 周波数の計算点数 |
| 最適化モード | `difference_only` または `opposite_sign` |

細胞固有のパラメータは、選択された細胞テンプレートから取得します。

    membrane_capacitance
    radius_m
    eps_c_relative
    sigma_c

溶液条件とシミュレーション条件は、GUIの入力欄から取得します。

## 数値探索の設計

探索は、`sigma_s` を対数スケールで離散化したグリッドサーチとして実装しています。

全体の流れは以下です。

1. 候補となる溶液導電率を生成する。

        sigma_s_candidates = logspace(log10(sigma_s_min), log10(sigma_s_max), num_sigma_points)

2. 周波数点を生成する。

        frequency_hz = logspace(log10(f_min), log10(f_max), num_frequency_points)

3. 各 `sigma_s` 候補に対して、2つの細胞の `Re[K]` 曲線を計算する。

        Re[K]_1(f, sigma_s)
        Re[K]_2(f, sigma_s)

4. 選択された最適化モードに従ってスコアを計算する。

5. 最も良いスコアを与える `sigma_s` と周波数 `f_opt` を選択する。

主な実装ファイルは以下です。

    src/dep_cm_sim/condition_optimizer.py
    src/dep_cm_sim/gui/parameter_window.py
    src/dep_cm_sim/gui/graph_window.py

## 差分最大モード

`difference_only` モードでは、2つの `Re[K]` 曲線の差が最大になる条件を探索します。

各 `sigma_s` 候補に対して、以下のスコアを計算します。

    score(f, sigma_s) = |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

そのうえで、周波数方向に最大となる点を求めます。

    f_opt = argmax_f |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

最後に、すべての `sigma_s` 候補の中で最もスコアが大きいものを選択します。

    sigma_s_opt = argmax_sigma_s max_f |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

このモードは、2つのCM因子曲線の数値的な差が最大となる条件を調べる場合に有用です。

ただし、このモードでは2つのDEP応答が逆符号であることは要求しません。そのため、最適条件において、両方の細胞が正のDEP、または両方の細胞が負のDEPを示す場合があります。

## 符号分離モード

`opposite_sign` モードでは、2つの細胞が反対向きのDEP応答を示す条件のみを探索対象にします。

有効な周波数点は、以下のいずれかを満たす点です。

    Re[K]_1 > 0 and Re[K]_2 < 0

または

    Re[K]_1 < 0 and Re[K]_2 > 0

この条件を満たす点に対してのみ、以下のスコアを計算します。

    score(f, sigma_s) = |Re[K]_1(f, sigma_s) - Re[K]_2(f, sigma_s)|

その中で、スコアが最大となる条件を選択します。

このモードは、DEP分離において特に重要です。なぜなら、一方の細胞を電場の強い領域へ引き寄せ、もう一方の細胞を電場の強い領域から遠ざける条件を直接探索できるためです。

探索範囲内に符号分離条件が存在しない場合は、エラーを出し、GUI上でもエラーダイアログを表示します。

## 探索範囲端の警告

最適な `sigma_s` が探索範囲の下限または上限にある場合、GUI上に警告を表示します。

これは、現在の探索範囲が狭く、より良い条件が探索範囲の外に存在する可能性を示します。

例えば、最適値が `sigma_s_min` に張り付いている場合は、以下のように探索範囲を広げて再計算することが有効です。

    sigma_s_min: 1.0e-5
    sigma_s_max: 1.0
    num_sigma_points: 50

## GUIでの使い方

パラメータウィンドウでは、以下を選択・入力できます。

- 細胞テンプレート1
- 細胞テンプレート2
- `sigma_s` 最小値
- `sigma_s` 最大値
- `sigma_s` 探索点数
- 最適化モード
  - 差分最大
  - 符号分離

最適化ボタンを押すと、GraphWindowが開き、以下が表示されます。

- 最適化された `sigma_s` における2つの `Re[K]` 曲線
- 最適周波数マーカー
- 最適化モード
- 最適点における `Re[K]_1` と `Re[K]_2`



---

# Experimental Data Comparison and Validation / 実験データ比較と検証可能性

## English

This simulator provides functions for comparing simulated Clausius-Mossotti factor curves with experimental data.

This part consists of:

- Phase 6: experimental data overlay
- Phase 7: quantitative error evaluation
- reliability, reproducibility, and validation documentation

Phase 6 allows experimental data to be displayed on the same graph as simulated `Re[K]` curves.  
Phase 7 allows experimental data and simulation results to be compared quantitatively using error metrics.

---

## Phase 6: Experimental Data Overlay

Experimental data can be loaded from CSV or entered manually through the GUI.

The standard experimental data CSV format is:

    frequency_hz,value,label,plot_style

The columns are:

| Column | Meaning |
|---|---|
| `frequency_hz` | Experimental frequency in Hz |
| `value` | Experimental value to compare with simulated `Re[K]` |
| `label` | Label used in the graph legend |
| `plot_style` | Display style for experimental data |

The supported `plot_style` values are:

| `plot_style` | Meaning |
|---|---|
| `scatter` | Points only |
| `line` | Line only |
| `scatter_line` | Points and line |

Main implementation files:

    src/dep_cm_sim/experimental_data.py
    src/dep_cm_sim/gui/experimental_data_window.py
    src/dep_cm_sim/gui/graph_window.py
    src/dep_cm_sim/gui/parameter_window.py
    tests/test_experimental_data.py

This makes it possible to save, reload, and visually compare experimental data with simulation curves.

---

## Phase 7: Quantitative Error Evaluation

The error evaluation function compares experimental data with the current simulation result.

The calculation flow is:

1. Read current simulation parameters from the parameter window.
2. Generate the simulation frequency array using `f_min`, `f_max`, and `num_points`.
3. Calculate the simulated `Re[K]` curve.
4. Load experimental data from CSV.
5. Interpolate simulated values at the experimental frequency points.
6. Calculate pointwise errors and summary metrics.
7. Save the error evaluation result as CSV.

The pointwise error is defined as:

    error = experimental_value - simulated_value

The absolute error is defined as:

    absolute_error = |experimental_value - simulated_value|

The summary metrics are:

| Metric | Meaning |
|---|---|
| MAE | Mean absolute error |
| RMSE | Root mean squared error |
| Maximum absolute error | Largest absolute error among evaluated points |
| Number of evaluated points | Number of experimental data points used for comparison |

The error evaluation CSV contains:

    frequency_hz,experimental_value,simulated_value,error,absolute_error

It also contains summary metrics:

    metric,value
    mae,...
    rmse,...
    max_absolute_error,...
    num_points,...

Main implementation files:

    src/dep_cm_sim/error_evaluation.py
    src/dep_cm_sim/gui/parameter_window.py
    tests/test_error_evaluation.py

---

# Reliability, Reproducibility, and Validation / 信頼性・再現性・検証可能性

## A. Software Implementation Reliability

Software implementation reliability is supported by:

- automated tests with `pytest`
- static code checking with `ruff`
- GitHub Actions CI
- Git commit history
- reproducible execution commands
- CSV-based input/output formats

The tests can be executed with:

    uv run pytest

At the time of this implementation, the test result is:

    71 passed

The lint check can be executed with:

    uv run ruff check .

At the time of this implementation, the lint result is:

    All checks passed

The application can be launched with:

    uv run dep-cm-sim

These checks support software-level reliability, but they do not prove scientific validity by themselves.

---

## B. Scientific Model Validity

Scientific model validity should be evaluated separately from software correctness.

This simulator supports scientific validation through:

- equation-level implementation of `Re[K]` in `src/dep_cm_sim/equations.py`
- reproduction of reference paper figures using the `論文図(a)〜(h)を再現` function
- parameter CSV export/import for traceability
- experimental data overlay
- quantitative error evaluation against experimental data

The CM factor calculation is separated from GUI code so that the numerical model can be inspected independently.

The reference figure reproduction function is useful for checking whether the implementation can reproduce known trends under corresponding parameter conditions.

Experimental data comparison provides both visual and quantitative checks using:

- pointwise error
- absolute error
- MAE
- RMSE
- maximum absolute error

However, scientific validity for a specific experiment still depends on:

- whether the input parameters match the experimental condition
- whether the model assumptions match the experimental setup
- whether the simulation agrees with measured data
- whether the experimental data quality is sufficient

Therefore, when this simulator is used for research or publication, the parameter set, experimental data, and error evaluation results should be reported together.

---

## 日本語

本シミュレータでは、シミュレーションされた Clausius-Mossotti 因子の実部 `Re[K]` と実験データを比較するために、以下の機能を実装している。

- Phase 6: 実験データ重ね描き
- Phase 7: 実験データとシミュレーションの誤差評価
- 信頼性・再現性・検証可能性の記録

---

## Phase 6: 実験データ重ね描き

実験データはCSVから読み込むか、GUI上で手入力できる。

標準CSV形式は以下である。

    frequency_hz,value,label,plot_style

各列の意味は以下である。

| 列 | 意味 |
|---|---|
| `frequency_hz` | 実験周波数 [Hz] |
| `value` | シミュレーションの `Re[K]` と比較する実験値 |
| `label` | グラフ凡例に表示するラベル |
| `plot_style` | 実験データの表示形式 |

`plot_style` には以下を指定できる。

| `plot_style` | 意味 |
|---|---|
| `scatter` | 点のみ |
| `line` | 線のみ |
| `scatter_line` | 点＋線 |

この機能により、実験データを保存・再読込し、シミュレーション曲線と視覚的に比較できる。

---

## Phase 7: 誤差評価

Phase 7では、実験データと現在のシミュレーション条件を定量的に比較する。

計算フローは以下である。

1. パラメータ入力ウィンドウから現在のシミュレーション条件を読み取る。
2. `f_min`, `f_max`, `num_points` から周波数配列を生成する。
3. 現在のパラメータで `Re[K]` 曲線を計算する。
4. 実験データCSVを読み込む。
5. 実験周波数点に対応するシミュレーション値を補間する。
6. 各点の誤差と絶対誤差を計算する。
7. MAE、RMSE、最大絶対誤差を計算する。
8. 誤差評価結果をCSVとして保存する。

誤差は以下で定義する。

    error = experimental_value - simulated_value

絶対誤差は以下で定義する。

    absolute_error = |experimental_value - simulated_value|

評価指標は以下である。

| 指標 | 意味 |
|---|---|
| MAE | 平均絶対誤差 |
| RMSE | 二乗平均平方根誤差 |
| 最大絶対誤差 | 評価点の中で最も大きい絶対誤差 |
| 評価点数 | 比較に使用した実験データ点数 |

---

## A. ソフトウェア実装としての信頼性

ソフトウェア実装としての信頼性は、以下によって確認できる。

- `pytest` による自動テスト
- `ruff` による静的解析
- GitHub ActionsによるCI
- Git履歴
- 再現可能な実行手順
- CSVによる入出力

テストは以下で実行できる。

    uv run pytest

現時点での結果は以下である。

    71 passed

静的解析は以下で実行できる。

    uv run ruff check .

現時点での結果は以下である。

    All checks passed

アプリケーションは以下で起動できる。

    uv run dep-cm-sim

---

## B. 科学モデルとしての妥当性

科学モデルとしての妥当性は、ソフトウェアテストだけでは証明できない。

本シミュレータでは、以下によって科学モデルの妥当性を確認できるようにしている。

- `src/dep_cm_sim/equations.py` における `Re[K]` の式実装
- `論文図(a)〜(h)を再現` 機能による既存論文図の再現
- パラメータCSVによる条件記録
- 実験データとの重ね描き
- 実験データとの定量的誤差評価

ただし、特定の実験条件における科学的妥当性は、実際の実験データとの比較によって確認する必要がある。

研究や論文で使用する場合は、使用したパラメータ、実験データ、誤差評価結果を併せて示すことが望ましい。


# Optimal Frequency Display / 最適周波数表示

## English

When exactly two curves are displayed in the graph window, the application can calculate and display the frequency where the two curves differ the most.

The optimal frequency is defined as the frequency that maximizes:

    |Re[K]_1 - Re[K]_2|

The result is shown on the graph as:

- a vertical dashed line at the optimal frequency
- an annotation showing `f_opt` and `|ΔRe[K]|`

This feature is intended to support visual comparison of two DEP response curves.

## 日本語

グラフWindow上に曲線が2本だけ表示されている場合、2曲線の差が最大となる周波数を計算し、グラフ上に表示できます。

本アプリケーションでは、最適周波数を以下が最大となる周波数として定義しています。

    |Re[K]_1 - Re[K]_2|

結果はグラフ上に以下の形で表示されます。

- 最適周波数位置の破線
- `f_opt` と `|ΔRe[K]|` を示す注釈

この機能は、2つのDEP応答曲線を比較するための補助機能です。


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

# Reproducing Reference Figure 1(a)–(h) / 参考文献 Figure 1(a)〜(h) の再現

## English

This application includes a reproduction mode for the frequency dependence of the real part of the CM factor shown in Figure 1 of the reference article.

The reproduction can be executed in two ways:

1. From the GUI by clicking `論文図(a)〜(h)を再現`
2. From the command line using the reproduction script

When executed from the GUI, the eight conductivity conditions are plotted in a new graph window. The existing PNG save and graph clear functions can also be used.

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

本アプリケーションには、参考文献 Figure 1 に示されているCM因子の実部の周波数依存性を再現する機能があります。

この再現機能は、以下の2通りで実行できます。

1. GUI上の「論文図(a)〜(h)を再現」ボタンから実行
2. コマンドラインで再現スクリプトを実行

GUIから実行した場合、8つの溶液導電率条件の曲線が新しいグラフWindowに重ね描きされます。既存のPNG保存機能やグラフクリア機能もそのまま使用できます。

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

# Reference / 参考文献

This simulator refers to Figure 1, "Frequency dependence of the real part of the CM factor acting on cells," in the following article.

本シミュレータは、以下の文献に掲載されている Figure 1「細胞に作用するCM因子の実部の周波数依存性」を参考にしています。

- Tomoyuki Yasukawa and Fumio Mizutani, "Rapid Detection Technique for Surface Antigen-Expressing Cells Using Dielectrophoresis," Electrochemistry, Vol. 82, No. 11, pp. 993–999, 2014.

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
    - src/dep_cm_sim/cell_templates.py
    - src/dep_cm_sim/plotter.py
    - src/dep_cm_sim/demo_plot.py
    - src/dep_cm_sim/reproduce_paper_figure.py
    - src/dep_cm_sim/parameter_io.py
    - src/dep_cm_sim/optimization.py
    - src/dep_cm_sim/paper_conditions.py
    - src/dep_cm_sim/gui/parameter_window.py
    - src/dep_cm_sim/gui/graph_window.py
    - tests/test_equations.py
    - tests/test_cell_templates.py
    - tests/test_optimization.py
    - tests/test_parameter_io.py
    - pyproject.toml
    - uv.lock
    - README.md

---

# Notes / 注意事項

## English

This software is intended for educational, simulation, and parameter-comparison purposes.

Before using simulation results for formal academic or engineering conclusions, confirm the model assumptions, parameter units, and equation definitions with the original literature and appropriate domain experts.

## 日本語

本ソフトウェアは、教育用途、シミュレーション、およびパラメータ比較を目的としたものです。

シミュレーション結果を正式な学術的・工学的結論に用いる前に、モデルの仮定、パラメータ単位、式の定義を原著論文および専門分野の知見に基づいて確認することを推奨します。
