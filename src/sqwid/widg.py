import math
import random
import subprocess
import os
import psutil
from time import sleep
from libqtile.widget import base

EM = "\u2014"
TWO_EM = "\u2e3a"
HEAVY_BOX = "\u2501"
DBL_HEAVY_BOX = "\u254d"
TRPL_HEAVY_BOX = "\u2505"


class SpawnWidget(base.ThreadPoolText):
    # defaults
    defaults = [
        ("markup", True, "Markup"),
        ("update_interval", 1, "C"),
        ("cmd", "echo 'Hello, World!'", ""),
    ]

    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(self.defaults)

    def _configure(self, qtile, bar) -> None:
        base.ThreadPoolText._configure(self, qtile, bar)

    def poll(self) -> str:
        output = subprocess.check_output(self.cmd, shell=True).decode().strip()
        return str(output)


class ProgressBar(base.ThreadPoolText):
    # defaults
    defaults = [
        ("markup", True, "Markup"),
        ("bar_char", EM, "Character used to build the bar."),
        ("line_char", "|", "Character used to for the level indicator."),
        ("update_interval", 1, "C"),
        ("bar_bg", "grey", ""),
        ("bar_fg", "blue", ""),
        (
            "check_output_cmd",
            "echo 50",
            "",
        ),
        ("max_value", 100, ""),
        ("scale", 10, ""),
    ]

    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(self.defaults)

    def _configure(self, qtile, bar) -> None:
        base.ThreadPoolText._configure(self, qtile, bar)

    def poll(self) -> str:
        cmd = self.check_output_cmd
        if str(type(cmd)) in ["<class 'function'>", "<class 'method'>"]:
            output = cmd()  # psutil.virtual_memory().percent
        elif type(cmd) in [list, str]:
            output = int(
                float(subprocess.check_output(cmd, shell=True).decode().strip())
            )
        elif cmd is None:
            raise TypeError
        else:
            raise NotImplementedError

        y = round(output / self.scale)
        ramp = self.bar_char * int((self.max_value / self.scale))
        if self.markup:
            line = f"<span color='{self.bar_fg}'>{ramp[:y]}</span>{self.      line_char}<span color='{self.bar_bg}'>{ramp[y:]}</span>"
        else:
            line = f"{ramp[:y]}{self.line_char}{ramp[y:]}"
        return line


class CpuRamp(base.ThreadPoolText):
    # defaults
    defaults = [
        ("markup", True, "Markup"),
        ("clr_low", "green", ""),
        ("clr_med", "yellow", ""),
        ("clr_high", "orange", ""),
        ("clr_crit", "red", ""),
        ("update_interval", 1, ""),
        ("sensitive", True, ""),
    ]

    def __init__(self, **config):
        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(self.defaults)

    def _configure(self, qtile, bar) -> None:
        base.ThreadPoolText._configure(self, qtile, bar)

    def poll(self) -> str:
        cpus = psutil.cpu_percent(1, percpu=True)
        return self._print_ramp(cpus)

    def _print_ramp(self, cpus):
        line = ""
        for x in cpus:
            bar = self._get_bar(x)
            line = f"{bar} {line}"
        return line

    def _get_bar(self, v: int | float):
        ramp = "▁▂▃▄▅▆▇█"
        bar = ""

        if self.sensitive:
            val = int(math.ceil(v / 10.0))
        else:
            val = int(round(v / 10.0))

        if val >= 8:
            bar = ramp[7]
        else:
            bar = ramp[val]

        if val >= 6:
            bar = f"<span color='{self.clr_crit}'>{bar}</span>"
        elif val >= 4:
            bar = f"<span color='{self.clr_high}'>{bar}</span>"
        elif val >= 2:
            bar = f"<span color='{self.clr_med}'>{bar}</span>"
        else:
            bar = f"<span color='{self.clr_low}'>{bar}</span>"

        return bar


class RamBar(ProgressBar):
    def __init__(self, **config):
        ProgressBar.__init__(self, **config)
        self.check_output_cmd = self._ram_percent

    def _ram_percent(self) -> float:
        return psutil.virtual_memory().percent
