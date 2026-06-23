"""
Generate Control Loop Schematic for Thesis
Creates LaTeX TikZ code for detailed control flow diagram.

Usage:
    python scripts/generate_control_loop_schematic.py

Output:
    academic/paper/thesis/figures/schematics/control_loop.tex (LaTeX source)
    academic/paper/thesis/figures/schematics/control_loop.pdf (Compiled PDF)
"""

import os

def generate_tikz_control_loop():
    """Generate LaTeX TikZ code for control loop schematic."""

    tikz_code = r"""\documentclass[tikz,border=10pt]{standalone}
\usepackage{tikz}
\usepackage{amsmath}
\usetikzlibrary{shapes,arrows,positioning,calc,decorations.pathreplacing}

\begin{document}

% Define block styles
\tikzstyle{block} = [draw, rectangle, minimum height=1.2cm, minimum width=2.5cm,
                     text width=2.3cm, text centered, rounded corners, thick]
\tikzstyle{sum} = [draw, circle, minimum size=0.8cm, thick]
\tikzstyle{input} = [coordinate]
\tikzstyle{output} = [coordinate]
\tikzstyle{pinstyle} = [pin edge={to-,thin,black}]
\tikzstyle{arrow} = [thick,->,>=stealth]

\begin{tikzpicture}[auto, node distance=2.5cm,>=latex']

    % Title
    \node[font=\Large\bfseries] at (0,8.5) {Sliding Mode Control Loop - DIP System};

    % Input
    \node[input] (ref) at (-8,5) {};
    \node[left of=ref, node distance=1.5cm] {\textbf{Reference:} $\theta_1^d=0, \theta_2^d=0$};

    % State Measurement
    \node[block, fill=blue!10] (sensor) at (-5,5) {State\\Measurement\\$\mathbf{x} = [x, \theta_1, \theta_2, \dot{x}, \dot{\theta}_1, \dot{\theta}_2]^T$};

    % Error Calculation
    \node[sum, fill=red!10] (sum1) at (-2,5) {$-$};

    % Sliding Surface
    \node[block, fill=green!10] (surface) at (1.5,5) {Sliding Surface\\$s_1 = \lambda_1\theta_1 + \dot{\theta}_1$\\$s_2 = \lambda_2\theta_2 + \dot{\theta}_2$};

    % Controller Variants (stacked)
    \node[block, fill=yellow!10, text width=3cm, minimum width=3.5cm] (controller) at (5.5,5) {
        \textbf{Control Law:}\\[0.1cm]
        \textit{Classical SMC:}\\
        $u = -K \text{sign}(s)$\\[0.1cm]
        \textit{STA-SMC:}\\
        $u = -K_1|s|^{1/2}\text{sgn}(s)$\\
        \hspace{0.5cm}$-K_2\int\text{sgn}(s)dt$\\[0.1cm]
        \textit{Adaptive:}\\
        $\hat{K}(t) = \gamma|s|$
    };

    % Boundary Layer / Saturation
    \node[block, fill=orange!10] (sat) at (9.5,5) {Saturation \&\\Boundary Layer\\$u = \text{sat}(u, F_{\max})$};

    % Plant Dynamics
    \node[block, fill=purple!10, minimum height=2cm, text width=3.5cm, minimum width=4cm] (plant) at (6,-0.5) {
        \textbf{DIP Dynamics}\\[0.1cm]
        $M(\mathbf{q})\ddot{\mathbf{q}} + C(\mathbf{q},\dot{\mathbf{q}})\dot{\mathbf{q}}$\\
        \hspace{1.5cm}$+ G(\mathbf{q}) = B u$\\[0.1cm]
        where $\mathbf{q} = [x, \theta_1, \theta_2]^T$\\
        Integration: RK45, $\Delta t = 0.001$s
    };

    % Integration Block
    \node[block, fill=cyan!10, below of=plant, node distance=2.5cm] (integrator) at (6,-3) {Numerical\\Integration\\$\dot{\mathbf{x}} = f(\mathbf{x}, u, t)$};

    % State Output
    \node[output] (stateout) at (6,-5.5) {};
    \node[right of=stateout, node distance=2cm] {\textbf{State Output}};

    % Feedback loop
    \draw[arrow] (ref) -- (sensor);
    \draw[arrow] (sensor) -- node[above] {$\mathbf{x}$} (sum1);
    \draw[arrow] (sum1) -- node[above] {$e$} (surface);
    \draw[arrow] (surface) -- node[above] {$s$} (controller);
    \draw[arrow] (controller) -- node[above] {$u_{\text{raw}}$} (sat);
    \draw[arrow] (sat) -- node[right, pos=0.3] {$u$} ++(0,-4.5) -- (plant);
    \draw[arrow] (plant) -- (integrator);
    \draw[arrow] (integrator) -- (stateout);

    % Feedback path
    \draw[arrow] (stateout) -| node[pos=0.1, right] {Feedback} ++(-12,0) |- (sensor);

    % Annotations
    \node[draw=none, fill=none, text width=4cm, font=\small] at (-5,1.5) {
        \textbf{Key Parameters:}\\
        $\lambda_1, \lambda_2$: Surface slopes\\
        $K, K_1, K_2$: Control gains\\
        $F_{\max} = 150$ N: Force limit\\
        $\Delta t = 0.001$ s: Sample time
    };

    % PSO Optimization (side annotation)
    \node[draw, dashed, thick, rectangle, rounded corners, fill=yellow!5,
          text width=3cm, font=\small] at (11,2) {
        \textbf{PSO Optimization}\\[0.1cm]
        Tunes controller\\gains offline:\\
        $K^*, \lambda^*$\\[0.1cm]
        30 particles\\
        50 iterations\\
        Multi-objective\\cost function
    };
    \draw[->, dashed, thick] (11,2.8) -- (controller.east);

    % Legend
    \node[draw=none, fill=none, text width=5cm, font=\scriptsize] at (1,-5) {
        \textbf{Legend:} \colorbox{blue!10}{Measurement} \colorbox{green!10}{Sliding Surface}
        \colorbox{yellow!10}{Controller} \colorbox{orange!10}{Saturation}
        \colorbox{purple!10}{Plant} \colorbox{cyan!10}{Integration}
    };

\end{tikzpicture}

\end{document}
"""

    # Save LaTeX source
    output_dir = 'academic/paper/thesis/figures/schematics'
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, 'control_loop.tex')

    with open(tex_path, 'w') as f:
        f.write(tikz_code)

    print(f"[OK] LaTeX TikZ code saved to: {tex_path}")

    # Compile to PDF
    import subprocess

    print("[INFO] Compiling TikZ to PDF...")
    try:
        # Change to output directory
        cwd = os.getcwd()
        os.chdir(output_dir)

        # Compile with pdflatex
        result = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'control_loop.tex'],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("[OK] PDF compilation successful")
            pdf_path = os.path.join(cwd, output_dir, 'control_loop.pdf')

            # Clean up auxiliary files
            for ext in ['.aux', '.log']:
                aux_file = f"control_loop{ext}"
                if os.path.exists(aux_file):
                    os.remove(aux_file)
                    print(f"[INFO] Cleaned up {aux_file}")

            os.chdir(cwd)

            # Check file size
            if os.path.exists(pdf_path):
                size_kb = os.path.getsize(pdf_path) / 1024
                print(f"[INFO] PDF file size: {size_kb:.1f} KB")

                if size_kb > 500:
                    print(f"[WARNING] File size exceeds 500 KB target")
                else:
                    print("[OK] File size within target (<500 KB)")

            return pdf_path
        else:
            print("[ERROR] PDF compilation failed")
            print(result.stdout)
            print(result.stderr)
            os.chdir(cwd)
            return None

    except FileNotFoundError:
        print("[ERROR] pdflatex not found. Please install LaTeX distribution (TeX Live or MiKTeX)")
        print("[INFO] LaTeX source saved at:", tex_path)
        print("[INFO] Compile manually: cd", output_dir, "&& pdflatex control_loop.tex")
        os.chdir(cwd)
        return None
    except Exception as e:
        print(f"[ERROR] Compilation failed: {e}")
        os.chdir(cwd)
        return None


if __name__ == '__main__':
    print("[INFO] Generating control loop schematic...")
    output = generate_tikz_control_loop()

    if output:
        print(f"[OK] Schematic generation complete: {output}")
    else:
        print("[WARNING] PDF not generated, but LaTeX source is available")
        print("[INFO] You can compile manually later")
