from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

async def generate_mood_chart_image(dates: list[str], moods: list[int]) -> bytes | None:
    if not dates or not moods or len(dates) != len(moods):
        return None

    try:
        x_dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
    except ValueError:
        return None

    fig, ax = plt.subplots(figsize=(12, 6), dpi=120)

    ax.plot(x_dates, moods, marker='o', linestyle='-', color='royalblue', linewidth=2.5, markersize=8)

    ax.set_title("Твоё настроение за период", fontsize=16, fontweight='bold')
    ax.set_xlabel("Дата", fontsize=12)
    ax.set_ylabel("Оценка (1–10)", fontsize=12)
    ax.set_ylim(0, 11)
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf.getvalue()