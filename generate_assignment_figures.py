"""
Generate all figures required for Assignment 1:
1. Part 1: Individual spectra for Cy3, Cy5, and Methylene Blue.
2. Part 2: Excitation wavelength sweep (400 to 700 nm) for Cy3, showing Kasha's rule and intensity profile.
3. Part 3: Three dyes overlaid at 450 nm, 550 nm, and 650 nm excitation wavelengths.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from plsim.samples import get_sample
from plsim.spectrometer import PLSpectrometer

FIG_DIR = Path("report_figures")
FIG_DIR.mkdir(exist_ok=True)

# Set clean styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

def generate_part1():
    print("Generating Part 1 figures...")
    dyes = [
        ("cy3", 550.0, 500.0, 750.0, "#d95f02"),
        ("cy5", 649.0, 600.0, 800.0, "#7570b3"),
        ("methylene-blue", 664.0, 550.0, 850.0, "#1b9e77"),
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    
    for ax, (key, lexc, lmin, lmax, color) in zip(axes, dyes):
        sample = get_sample(key)
        spec = PLSpectrometer(sample=sample, scatter_fraction=0.005)
        scan = spec.acquire(lambda_exc_nm=lexc, lambda_min_nm=lmin, lambda_max_nm=lmax, dlambda_nm=1.0)
        
        ax.plot(scan.wavelengths_nm, scan.photocurrent, color=color, lw=2.2, label=f"PL Signal ({sample.name})")
        ax.axvline(lexc, color="gray", linestyle="--", alpha=0.7, label=f"$\\lambda_{{exc}} = {lexc:.0f}$ nm")
        ax.set_title(f"{sample.name}\n($\\lambda_{{exc}} = {lexc:.0f}$ nm, $\\Phi = {sample.quantum_yield}$)")
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Photocurrent (a.u.)")
        ax.legend(loc="upper right")
        
        # Individual high-res plot for each dye
        ind_fig, ind_ax = plt.subplots(figsize=(6.5, 4.2), constrained_layout=True)
        ind_ax.plot(scan.wavelengths_nm, scan.photocurrent, color=color, lw=2.2, label=f"{sample.name} Detected PL")
        ind_ax.axvline(lexc, color="gray", linestyle="--", alpha=0.7, label=f"Excitation $\\lambda_{{exc}} = {lexc:.0f}$ nm")
        ind_ax.set_title(f"Simulated PL Spectrum of {sample.name}\n($\\lambda_{{exc}} = {lexc:.0f}$ nm, Detection: {lmin:.0f}-{lmax:.0f} nm)")
        ind_ax.set_xlabel("Wavelength $\\lambda$ (nm)")
        ind_ax.set_ylabel("Photodetector Current (relative a.u.)")
        ind_ax.legend(loc="upper right")
        ind_fig.savefig(FIG_DIR / f"part1_{key}.png", dpi=300)
        plt.close(ind_fig)
        
    fig.suptitle("Part 1: Simulated PL Spectra of Cyanine & Phenothiazine Organic Dyes", fontsize=15, fontweight="bold")
    fig.savefig(FIG_DIR / "part1_combined_overview.png", dpi=300)
    plt.close(fig)


def generate_part2():
    print("Generating Part 2 figures (Cy3 excitation sweep 400 - 700 nm)...")
    sample = get_sample("cy3")
    spec = PLSpectrometer(sample=sample, scatter_fraction=0.0) # ideal to highlight emission physics
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), constrained_layout=True)
    
    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(vmin=450, vmax=600)
    
    # Selected representative excitation wavelengths
    selected_curves = [450, 480, 510, 530, 550, 565, 580, 610]
    for lexc in selected_curves:
        scan = spec.acquire(lambda_exc_nm=lexc, lambda_min_nm=500.0, lambda_max_nm=750.0, dlambda_nm=1.0)
        c = cmap(norm(lexc))
        ax1.plot(scan.wavelengths_nm, scan.photocurrent, color=c, lw=2.0, 
                 label=f"$\\lambda_{{exc}} = {lexc}$ nm")
        
    ax1.set_title("Emission Spectra at Varying Excitation $\\lambda_{exc}$\n(Peak position remains constant at 570 nm — Kasha's Rule)")
    ax1.set_xlabel("Emission Wavelength $\\lambda$ (nm)")
    ax1.set_ylabel("Photocurrent (a.u.)")
    ax1.axvline(570.0, color="red", linestyle=":", lw=1.5, label="Emission Peak (570 nm)")
    ax1.legend(loc="upper right", framealpha=0.9, fontsize=9)
    
    # Calculate peak PL intensity across continuous range 400 - 700 nm
    fine_lexc = np.linspace(400, 700, 151)
    peak_intensities = []
    for lexc in fine_lexc:
        scan = spec.acquire(lambda_exc_nm=lexc, lambda_min_nm=565.0, lambda_max_nm=575.0, dlambda_nm=0.5)
        peak_intensities.append(np.max(scan.photocurrent))
        
    peak_intensities = np.array(peak_intensities)
    
    # Plot excitation profile vs theoretical absorbance
    ax2.plot(fine_lexc, peak_intensities, color="#d95f02", lw=2.5, label="Peak PL Intensity (at 570 nm)")
    
    absorbance = np.array([sample.absorbance(l) for l in fine_lexc])
    ax2_twin = ax2.twinx()
    ax2_twin.plot(fine_lexc, absorbance, color="#1f77b4", linestyle="--", lw=1.8, label="Sample Absorbance $A(\\lambda)$")
    ax2_twin.set_ylabel("Absorbance (O.D.)", color="#1f77b4")
    ax2_twin.tick_params(axis='y', labelcolor="#1f77b4")
    ax2_twin.grid(False)
    
    ax2.set_title("PL Peak Intensity vs. Excitation Wavelength (400 - 700 nm)\n(Experimental Excitation Spectrum Matches Absorption Band)")
    ax2.set_xlabel("Excitation Wavelength $\\lambda_{exc}$ (nm)")
    ax2.set_ylabel("Photocurrent at 570 nm (a.u.)", color="#d95f02")
    ax2.tick_params(axis='y', labelcolor="#d95f02")
    
    lines_1, labels_1 = ax2.get_legend_handles_labels()
    lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper right")
    
    fig.suptitle("Part 2: Systematic Excitation Wavelength Variation for Cy3 (400 - 700 nm)", fontsize=14, fontweight="bold")
    fig.savefig(FIG_DIR / "part2_cy3_excitation_sweep.png", dpi=300)
    plt.close(fig)


def generate_part3():
    print("Generating Part 3 figures (3 Dyes at 450, 550, 650 nm)...")
    excitation_wavelengths = [450.0, 550.0, 650.0]
    dye_keys = ["cy3", "cy5", "methylene-blue"]
    dye_colors = {"cy3": "#d95f02", "cy5": "#7570b3", "methylene-blue": "#1b9e77"}
    dye_names = {"cy3": "Cy3", "cy5": "Cy5", "methylene-blue": "Methylene Blue"}
    
    # 3 subplots side by side
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.0), constrained_layout=True, sharey=True)
    
    for ax, lexc in zip(axes, excitation_wavelengths):
        ax.axvline(lexc, color="black", linestyle="--", alpha=0.5, label=f"$\\lambda_{{exc}} = {lexc:.0f}$ nm")
        for key in dye_keys:
            sample = get_sample(key)
            spec = PLSpectrometer(sample=sample, scatter_fraction=0.0)
            scan = spec.acquire(lambda_exc_nm=lexc, lambda_min_nm=480.0, lambda_max_nm=820.0, dlambda_nm=1.0)
            
            ax.plot(scan.wavelengths_nm, scan.photocurrent, color=dye_colors[key], 
                    lw=2.2, label=f"{dye_names[key]} ($\\Phi={sample.quantum_yield}$)")
            
        ax.set_title(f"Excitation $\\lambda_{{exc}} = {lexc:.0f}$ nm")
        ax.set_xlabel("Emission Wavelength $\\lambda$ (nm)")
        if ax == axes[0]:
            ax.set_ylabel("PL Intensity (Photocurrent, a.u.)")
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9.5)
        ax.set_xlim(480, 820)
        
    fig.suptitle("Part 3: Comparative Emission Spectra of Cy3, Cy5, and Methylene Blue\n(Equal Optical Path & Peak Absorbance, Excitation at 450, 550, and 650 nm)", 
                 fontsize=14, fontweight="bold")
    fig.savefig(FIG_DIR / "part3_three_dyes_comparison.png", dpi=300)
    plt.close(fig)

    # Single combined canvas
    fig_single, ax_s = plt.subplots(figsize=(10.5, 5.5), constrained_layout=True)
    linestyles = {450.0: ":", 550.0: "-", 650.0: "--"}
    for lexc in excitation_wavelengths:
        for key in dye_keys:
            sample = get_sample(key)
            spec = PLSpectrometer(sample=sample, scatter_fraction=0.0)
            scan = spec.acquire(lambda_exc_nm=lexc, lambda_min_nm=480.0, lambda_max_nm=820.0, dlambda_nm=1.0)
            ax_s.plot(scan.wavelengths_nm, scan.photocurrent, color=dye_colors[key], 
                      linestyle=linestyles[lexc], lw=1.8, 
                      label=f"{dye_names[key]} ($\\lambda_{{exc}}={lexc:.0f}$ nm)")
            
    ax_s.set_title("Part 3: Multi-Dye & Multi-Wavelength Overlay (450, 550, 650 nm)")
    ax_s.set_xlabel("Wavelength $\\lambda$ (nm)")
    ax_s.set_ylabel("Photocurrent (a.u.)")
    ax_s.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    fig_single.savefig(FIG_DIR / "part3_single_canvas_overlay.png", dpi=300)
    plt.close(fig_single)

if __name__ == "__main__":
    generate_part1()
    generate_part2()
    generate_part3()
    print("All assignment figures generated successfully!")
