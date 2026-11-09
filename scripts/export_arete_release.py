#!/usr/bin/env python3
"""Export the Arete snapshot with the shared evaluation release exporter."""
from pathlib import Path
from export_evaluation_release import export

if __name__ == '__main__':
    export(Path(__file__).resolve().parents[1] / 'eval/arete-01')
