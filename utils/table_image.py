import asyncio
import pandas as pd
from copy import deepcopy
from io import BytesIO
from threading import Lock
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


_render_lock = Lock()


def _render_table(data: dict, size: tuple[int, int]) -> bytes:
    with _render_lock:
        table = pd.DataFrame.from_dict(data)
        figure = Figure(figsize=size, facecolor='#4f4f4f')
        FigureCanvasAgg(figure)
        try:
            axes = figure.subplots()
            axes.axis('tight')
            axes.axis('off')
            if table.empty:
                axes.text(0.5, 0.5, 'Нет данных', ha='center', va='center', color='white')
            else:
                axes.table(
                    cellText=table.values,
                    colLabels=table.columns,
                    loc='center',
                    cellLoc='center',
                    rowLoc='center',
                    colColours=['YellowGreen'] * len(table.columns),
                )
            with BytesIO() as image:
                figure.savefig(image, format='png', bbox_inches='tight')
                return image.getvalue()
        finally:
            figure.clear()


async def render_table(data: dict, size: tuple[int, int] = (6, 4)) -> bytes:
    snapshot = deepcopy(data)
    return await asyncio.to_thread(_render_table, snapshot, size)
