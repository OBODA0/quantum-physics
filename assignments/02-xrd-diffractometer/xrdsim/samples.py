"""The phase database: cell, symmetry-expanded basis and the source of each number.

Coordinates are fractions of the cell edge. Every site list below is the full basis of
the conventional cell, already expanded by the space-group operations, so the structure
factor needs no symmetry engine. Lattice constants carry the record they came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Site:
    element: str
    x: float
    y: float
    z: float
    occupancy: float = 1.0
    b_iso: float = 0.5          # square angstrom; a stated assumption for every phase


@dataclass(frozen=True)
class Phase:
    key: str
    name: str
    formula: str
    space_group: str
    a: float
    c: float | None = None
    b: float | None = None
    hexagonal: bool = False
    sites: tuple[Site, ...] = field(default_factory=tuple)
    source: str = ""

    @property
    def system(self) -> str:
        if self.hexagonal:
            return "hexagonal"
        if self.b is not None:
            return "orthorhombic"
        return "cubic" if self.c is None else "tetragonal"

    def cell_kwargs(self) -> dict:
        return {"a": self.a, "b": self.b, "c": self.c, "hexagonal": self.hexagonal}

    @property
    def volume(self) -> float:
        """Conventional-cell volume in cubic angstrom."""
        if self.hexagonal:
            return self.a * self.a * self.c * 0.8660254037844386
        if self.b is None and self.c is None:
            return self.a ** 3
        return self.a * (self.b or self.a) * self.c


def _fcc(element: str, b_iso: float = 0.5) -> tuple[Site, ...]:
    return tuple(Site(element, x, y, z, b_iso=b_iso) for x, y, z in
                 [(0, 0, 0), (0, .5, .5), (.5, 0, .5), (.5, .5, 0)])


def _rocksalt(cation: str, anion: str) -> tuple[Site, ...]:
    sites = list(_fcc(cation))
    sites += [Site(anion, x + .5, y, z) for x, y, z in
              [(0, 0, 0), (0, .5, .5), (.5, 0, .5), (.5, .5, 0)]]
    return tuple(sites)


PHASES: dict[str, Phase] = {
    "si": Phase(
        key="si", name="Silicon", formula="Si", space_group="Fd-3m (227)",
        a=5.431144, sites=tuple(
            [Site("Si", x, y, z) for x, y, z in
             [(0, 0, 0), (0, .5, .5), (.5, 0, .5), (.5, .5, 0),
              (.25, .25, .25), (.25, .75, .75), (.75, .25, .75), (.75, .75, .25)]]),
        source="NIST SRM 640f certificate [14], a = 5.431144(8) A at 22.5 C"),
    "al": Phase(
        key="al", name="Aluminium", formula="Al", space_group="Fm-3m (225)",
        a=4.0495, sites=_fcc("Al"),
        source="Cullity & Stock [3], Appendix 3 (20 C: a = 4.0495 A)"),
    "cu": Phase(
        key="cu", name="Copper", formula="Cu", space_group="Fm-3m (225)",
        a=3.6149, sites=_fcc("Cu"),
        source="Cullity & Stock [3], Appendix 3 (20 C: a = 3.615 A)"),
    "fe": Phase(
        key="fe", name="alpha-Iron", formula="Fe", space_group="Im-3m (229)",
        a=2.8665, sites=(Site("Fe", 0, 0, 0), Site("Fe", .5, .5, .5)),
        source="Cullity & Stock [3], Appendix 3 (20 C: a = 2.8665 A)"),
    "nacl": Phase(
        key="nacl", name="Rock salt", formula="NaCl", space_group="Fm-3m (225)",
        a=5.6402, sites=_rocksalt("Na", "Cl"),
        source="ICDD PDF 05-0628 [13] / Cullity & Stock [3] (26 C: a = 5.6402 A)"),
    "mgo": Phase(
        key="mgo", name="Periclase", formula="MgO", space_group="Fm-3m (225)",
        a=4.2112, sites=_rocksalt("Mg", "O"),
        source="ICDD PDF 04-0829 [13] (26 C: a = 4.2112 A)"),
    "zno": Phase(
        key="zno", name="Zincite", formula="ZnO", space_group="P63mc (186)",
        a=3.2494, c=5.2038, hexagonal=True, sites=(
            Site("Zn", 1/3, 2/3, 0.0), Site("Zn", 2/3, 1/3, 0.5),
            Site("O", 1/3, 2/3, 0.3830), Site("O", 2/3, 1/3, 0.8830)),
        source=("Kihara & Donnay (1985) [15], COD 9004180 [12] "
                "(293 K: a = 3.2494, c = 5.2038 A; u(O) = 0.3830)")),
    "tio2-rutile": Phase(
        key="tio2-rutile", name="Rutile", formula="TiO2", space_group="P42/mnm (136)",
        a=4.5937, c=2.9587, sites=(
            Site("Ti", 0, 0, 0), Site("Ti", .5, .5, .5),
            Site("O", .3047, .3047, 0), Site("O", .6953, .6953, 0),
            Site("O", .8047, .1953, .5), Site("O", .1953, .8047, .5)),
        source=("Burdett et al. (1987) [16] "
                "(295 K neutron: a = 4.5937, c = 2.9587 A; u(O) = 0.3047)")),
    "tio2-anatase": Phase(
        key="tio2-anatase", name="Anatase", formula="TiO2", space_group="I41/amd (141)",
        a=3.7845, c=9.5143, sites=(
            Site("Ti", 0, 0, 0), Site("Ti", 0, .5, .25),
            Site("Ti", .5, .5, .5), Site("Ti", .5, 0, .75),
            Site("O", 0, 0, .2079), Site("O", 0, .5, .4579),
            Site("O", .5, .5, .7079), Site("O", .5, 0, .9579),
            Site("O", 0, .5, .0421), Site("O", 0, 0, .7921),
            Site("O", .5, 0, .5421), Site("O", .5, .5, .2921)),
        source=("Burdett et al. (1987) [16] "
                "(295 K neutron: a = 3.7845, c = 9.5143 A; z(O) = 0.2079)")),
}


def get_phase(key: str) -> Phase:
    aliases = {"bcc": "fe", "fcc": "cu"}
    key = aliases.get(key, key)
    if key == "sc":
        return simple_cubic()
    try:
        return PHASES[key]
    except KeyError:
        choices = ", ".join(sorted(list(PHASES) + ["sc", "bcc", "fcc", "amorphous"]))
        raise KeyError(f"unknown phase {key!r}; choose from {choices}") from None


def simple_cubic(a: float = 3.359, element: str = "Cu") -> Phase:
    """Generic simple-cubic (Pm-3m) 1-atom model at cell edge `a` (default 3.359 A)."""
    return Phase(
        key="sc", name="Simple cubic", formula=f"{element} (SC)",
        space_group="Pm-3m (221)", a=a, sites=(Site(element, 0, 0, 0),),
        source=f"generic simple-cubic 1-atom model (Pm-3m), a = {a:.4f} A",
    )

