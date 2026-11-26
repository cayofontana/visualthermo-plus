"""Exploratory, reference-free characterization of recorded raw Y16 sequences.

Statistics are descriptive: temporal variation is not synonymous with sensor noise.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


class ThermalNoiseAnalyzer:
    def __init__(self, path):
        self.path = Path(path)
        with np.load(self.path, allow_pickle=False) as archive:
            if not {'frames', 'timestamps'}.issubset(archive.files):
                raise ValueError('Arquivo NPZ precisa conter frames e timestamps.')
            self.frames = archive['frames']
            self.timestamps = archive['timestamps']
        if self.frames.ndim != 3 or self.frames.dtype != np.uint16:
            raise ValueError('Esperados quadros Y16 uint16 com dimensões (N, H, W).')
        if len(self.frames) < 2 or len(self.timestamps) != len(self.frames):
            raise ValueError('Sequência precisa ter ao menos dois quadros e timestamps correspondentes.')
        self.seconds = self._relative_seconds(self.timestamps)
        self._stats = None

    @staticmethod
    def _relative_seconds(timestamps):
        from datetime import datetime
        times = [datetime.fromisoformat(str(t)) for t in timestamps]
        if any(t.tzinfo is None for t in times):
            raise ValueError('Timestamps devem conter informação de fuso horário.')
        result = np.array([(t - times[0]).total_seconds() for t in times], dtype=float)
        if np.any(np.diff(result) <= 0):
            raise ValueError('Timestamps precisam estar em ordem estritamente crescente.')
        return result

    def analyze(self):
        if self._stats is not None:
            return self._stats
        f = self.frames.astype(np.float64)
        frame_means = f.mean(axis=(1, 2))
        temporal_mean = f.mean(axis=0)
        temporal_std = f.std(axis=0, ddof=1)
        centered = f - frame_means[:, None, None]
        residual_std = centered.std(axis=0, ddof=1)
        frame_delta = np.diff(frame_means)
        gaps = np.diff(self.seconds)
        self._stats = {
            'frame_means': frame_means,
            'temporal_mean': temporal_mean,
            'temporal_std': temporal_std,
            'residual_std': residual_std,
            'frame_delta': frame_delta,
            'gaps': gaps,
        }
        return self._stats

    def summary(self):
        s = self.analyze()
        duration = float(self.seconds[-1])
        gaps = s['gaps']
        # Robust exploratory threshold, not an automatic NUC classifier.
        differences = s['frame_delta']
        center = np.median(differences)
        mad = np.median(np.abs(differences - center))
        threshold = max(10.0, 6 * 1.4826 * mad)
        candidates = np.flatnonzero(np.abs(differences - center) > threshold) + 1
        return {
            'source': self.path.name,
            'frame_count': int(len(self.frames)),
            'height': int(self.frames.shape[1]),
            'width': int(self.frames.shape[2]),
            'dtype': str(self.frames.dtype),
            'duration_s': duration,
            'effective_fps': float((len(self.frames) - 1) / duration),
            'global_mean_y16': float(s['frame_means'].mean()),
            'temporal_std_mean_y16': float(s['temporal_std'].mean()),
            'temporal_std_min_y16': float(s['temporal_std'].min()),
            'temporal_std_max_y16': float(s['temporal_std'].max()),
            'spatial_mean_removed_std_mean_y16': float(s['residual_std'].mean()),
            'frame_mean_min_y16': float(s['frame_means'].min()),
            'frame_mean_max_y16': float(s['frame_means'].max()),
            'largest_timestamp_gap_s': float(gaps.max()),
            'gaps_over_0_3s': int(np.count_nonzero(gaps > .3)),
            'candidate_global_jump_frame_indices': candidates.tolist(),
            'candidate_threshold_y16': float(threshold),
            'caveat': 'Variabilidade temporal inclui possíveis mudanças da cena, deriva e NUC; candidatos não são NUC confirmados.',
        }

    def export(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        s = self.analyze()
        report = self.summary()
        (output_dir / 'summary.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        with (output_dir / 'timeline.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(['frame_index', 'elapsed_seconds', 'spatial_mean_y16', 'delta_spatial_mean_y16', 'timestamp_gap_seconds'])
            for i, (t, mean) in enumerate(zip(self.seconds, s['frame_means'])):
                writer.writerow([i, float(t), float(mean), '' if i == 0 else float(s['frame_delta'][i-1]), '' if i == 0 else float(s['gaps'][i-1])])
        for name in ('temporal_mean', 'temporal_std', 'residual_std'):
            np.save(output_dir / f'{name}.npy', s[name])
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(self.seconds, s['frame_means'], linewidth=1)
        ax.set(xlabel='Tempo decorrido (s)', ylabel='Média espacial (Y16)', title='Evolução da média espacial')
        ax.grid(alpha=.25)
        fig.tight_layout()
        fig.savefig(output_dir / 'timeline.png', dpi=160)
        plt.close(fig)
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
        for ax, key, title in zip(axes, ('temporal_mean', 'temporal_std', 'residual_std'), ('Média temporal Y16', 'Desvio-padrão temporal', 'Desvio-padrão após remoção da média espacial')):
            im = ax.imshow(s[key], cmap='inferno')
            ax.set_title(title, fontsize=9)
            ax.axis('off')
            fig.colorbar(im, ax=ax, fraction=.046, pad=.04)
        fig.tight_layout()
        fig.savefig(output_dir / 'maps.png', dpi=160)
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(self.seconds[1:], s['frame_delta'], linewidth=.7)
        ax.set(xlabel='Tempo decorrido (s)', ylabel='Diferença da média espacial (Y16)', title='Variação entre quadros consecutivos')
        ax.grid(alpha=.25)
        fig.tight_layout()
        fig.savefig(output_dir / 'frame_differences.png', dpi=160)
        plt.close(fig)
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description='Análise exploratória de sequências Y16 do VisualThermo+.')
    parser.add_argument('sequences', nargs='+', type=Path, help='Arquivos .npz a analisar')
    parser.add_argument('--output', type=Path, default=Path('data/analysis'))
    args = parser.parse_args(argv)
    summaries = []
    for index, path in enumerate(args.sequences, 1):
        folder = args.output / f'{index:02d}_{path.stem}'
        report = ThermalNoiseAnalyzer(path).export(folder)
        summaries.append(report)
        print(f"{path.name}: {report['frame_count']} quadros; desvio temporal médio {report['temporal_std_mean_y16']:.2f} Y16 -> {folder}")
    if len(summaries) > 1:
        with (args.output / 'comparison.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=[key for key in summaries[0] if key not in ('candidate_global_jump_frame_indices', 'caveat')])
            writer.writeheader()
            writer.writerows({key: value for key, value in report.items() if key in writer.fieldnames} for report in summaries)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
