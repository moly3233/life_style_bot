from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
from typing import List, Union

from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
from typing import List, Union

async def generate_mood_chart_image(
    dates: List[str],                      # ← теперь только строки '%Y-%m-%d'
    values: List[Union[int, float]],
    title: str,
    x_label: str,
    y_label: str,
    ylim_bottom: float = None,
    ylim_top: float = None
) -> bytes | None:
    if not dates or not values or len(dates) != len(values):
        print("Нет данных или длина не совпадает")
        return None

    # Парсим строки в datetime (теперь всё в строках — должно работать)
    try:
        x_dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
    except ValueError as e:
        print(f"Ошибка формата даты: {e}")
        return None

    if len(x_dates) < 2:
        print("Слишком мало точек для графика")
        return None

    fig, ax = plt.subplots(figsize=(12, 6), dpi=120)

    ax.plot(
        x_dates,
        values,
        marker='o',
        linestyle='-',
        color='royalblue',
        linewidth=2.5,
        markersize=8,
        label=y_label
    )

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Диапазон по Y
    if ylim_bottom is not None and ylim_top is not None:
        ax.set_ylim(ylim_bottom, ylim_top)
    else:
        y_min = min(values)
        y_max = max(values)
        y_range = y_max - y_min if y_max > y_min else 1
        ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)

    return buf.getvalue()