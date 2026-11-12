"""Interactive Tkinter + Matplotlib GUI for the DLS Nanoparticle Simulator."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .plot import plot_dls_dashboard
from .simulator import DLSInputs, simulate_dls
from .solvents import list_solvents


class DLSSimulatorGUI:
    """Interactive desktop GUI implementing the 6 whiteboard inputs & 3 outputs."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Dynamic Light Scattering (DLS) Simulator — Task 3")
        self.root.geometry("1380x860")

        self.solvent_var = tk.StringVar(value="water")
        self.ri_var = tk.DoubleVar(value=1.590)
        self.size_var = tk.DoubleVar(value=50.0)
        self.sigma_var = tk.DoubleVar(value=0.12)
        self.shape_var = tk.StringVar(value="lognormal")
        self.agg_var = tk.DoubleVar(value=0.08)
        self.temp_var = tk.DoubleVar(value=25.0)
        self.pdi_status_var = tk.StringVar(value="PDI = --")

        self._build_layout()
        self.update_simulation()

    def _build_layout(self) -> None:
        ctrl = ttk.LabelFrame(
            self.root, text="DLS Whiteboard Inputs", padding=(12, 10)
        )
        ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # 1. Select solvent (water, ethanol, ...)
        ttk.Label(ctrl, text="1. Select Solvent:").pack(anchor="w", pady=(4, 2))
        solvent_cb = ttk.Combobox(
            ctrl,
            textvariable=self.solvent_var,
            values=list_solvents(),
            state="readonly",
            width=18,
        )
        solvent_cb.pack(anchor="w", pady=(0, 8))
        solvent_cb.bind("<<ComboboxSelected>>", lambda _e: self.update_simulation())

        # 2. Refractive index of the particle
        ttk.Label(ctrl, text="2. Particle Refractive Index (n_p):").pack(
            anchor="w", pady=(4, 2)
        )
        ri_scale = tk.Scale(
            ctrl,
            from_=1.33,
            to=2.60,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.ri_var,
            length=210,
            command=lambda _v: self.update_simulation(),
        )
        ri_scale.pack(anchor="w", pady=(0, 8))

        # 3. Size of the particle (nm)
        ttk.Label(ctrl, text="3. Particle Size d_0 (nm):").pack(
            anchor="w", pady=(4, 2)
        )
        size_scale = tk.Scale(
            ctrl,
            from_=2.0,
            to=500.0,
            resolution=1.0,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            length=210,
            command=lambda _v: self.update_simulation(),
        )
        size_scale.pack(anchor="w", pady=(0, 8))

        # 4. Size distribution of the particle
        ttk.Label(ctrl, text="4. Size Distribution Width (sigma/d_0):").pack(
            anchor="w", pady=(4, 2)
        )
        sigma_scale = tk.Scale(
            ctrl,
            from_=0.02,
            to=0.55,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.sigma_var,
            length=210,
            command=lambda _v: self.update_simulation(),
        )
        sigma_scale.pack(anchor="w", pady=(0, 4))

        ttk.Label(ctrl, text="   Distribution Shape:").pack(anchor="w")
        shape_cb = ttk.Combobox(
            ctrl,
            textvariable=self.shape_var,
            values=["lognormal", "gaussian"],
            state="readonly",
            width=18,
        )
        shape_cb.pack(anchor="w", pady=(0, 8))
        shape_cb.bind("<<ComboboxSelected>>", lambda _e: self.update_simulation())

        # 5. Aggregation parameter
        ttk.Label(ctrl, text="5. Aggregation Parameter (alpha_agg):").pack(
            anchor="w", pady=(4, 2)
        )
        agg_scale = tk.Scale(
            ctrl,
            from_=0.00,
            to=0.80,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.agg_var,
            length=210,
            command=lambda _v: self.update_simulation(),
        )
        agg_scale.pack(anchor="w", pady=(0, 8))

        # 6. Temperature (C)
        ttk.Label(ctrl, text="6. Temperature T (deg C):").pack(
            anchor="w", pady=(4, 2)
        )
        temp_scale = tk.Scale(
            ctrl,
            from_=5.0,
            to=70.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            variable=self.temp_var,
            length=210,
            command=lambda _v: self.update_simulation(),
        )
        temp_scale.pack(anchor="w", pady=(0, 12))

        # PDI status readout box
        pdi_lbl = ttk.Label(
            ctrl,
            textvariable=self.pdi_status_var,
            font=("Consolas", 10, "bold"),
            wraplength=210,
        )
        pdi_lbl.pack(anchor="w", pady=(8, 12))

        ttk.Button(
            ctrl, text="Re-run Simulation", command=self.update_simulation
        ).pack(fill=tk.X, pady=4)

        # Plot frame
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.fig: Figure = plot_dls_dashboard(
            simulate_dls(DLSInputs()), out_path=None, dpi=110
        )
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def current_inputs(self) -> DLSInputs:
        """Collect current slider and dropdown values into DLSInputs."""
        return DLSInputs(
            solvent=self.solvent_var.get(),
            particle_ri=float(self.ri_var.get()),
            size_nm=float(self.size_var.get()),
            size_std_rel=float(self.sigma_var.get()),
            aggregation=float(self.agg_var.get()),
            temperature_c=float(self.temp_var.get()),
            dist_shape=self.shape_var.get(),
        )

    def update_simulation(self) -> None:
        """Recompute DLS outputs and refresh the Matplotlib canvas."""
        outputs = simulate_dls(self.current_inputs())
        cum = outputs.cumulants
        self.pdi_status_var.set(
            f"Z-Avg D_z = {cum.z_average_nm:.1f} nm\n"
            f"PDI = {cum.pdi:.4f}\n"
            f"{cum.quality_verdict}"
        )

        import matplotlib.pyplot as plt

        plt.close(self.fig)
        self.fig = plot_dls_dashboard(outputs, out_path=None, dpi=110)
        self.canvas.figure = self.fig
        self.canvas.draw_idle()


def launch_gui() -> None:
    """Launch the interactive Tkinter DLS simulator window."""
    root = tk.Tk()
    _app = DLSSimulatorGUI(root)
    root.mainloop()


def save_gui_snapshot(
    out_path: str | Path,
    inputs: DLSInputs | None = None,
) -> Path:
    """Render the dashboard figure used by the GUI to a PNG file."""
    import matplotlib.pyplot as plt

    sim_inputs = inputs if inputs is not None else DLSInputs()
    outputs = simulate_dls(sim_inputs)
    target = Path(out_path)
    fig = plot_dls_dashboard(outputs, out_path=target, dpi=200)
    plt.close(fig)
    return target
