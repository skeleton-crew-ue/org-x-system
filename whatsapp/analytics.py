import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .parsers import parse_export

_vader = SentimentIntensityAnalyzer()

BURST_WINDOW_SECONDS = 120
BURST_MESSAGE_THRESHOLD = 5


def sentiment_analysis(df):
    real_mask = ~df["is_system"]
    df.loc[real_mask, "sentiment"] = df.loc[real_mask, "body"].apply(
        lambda text: _vader.polarity_scores(text)["compound"]
    )


def compute_summary(df):
    real = df[~df["is_system"]]
    return {
        "total_messages": int(len(real)),
        "unique_senders": int(real["sender"].nunique()),
        "media_message_count": int(real["is_media"].sum()),
        "date_range": {
            "first": real["timestamp"].min().date().isoformat(),
            "last": real["timestamp"].max().date().isoformat(),
        },
        "text_message_count": int((~real["is_media"]).sum()),
    }


def compute_peak_hours(df):
    counts = df[~df["is_system"]]["timestamp"].dt.hour.value_counts().reindex(range(24), fill_value=0)
    return [{"hour": int(h), "count": int(c)} for h, c in counts.items()]


def compute_per_user(df):
    real = df[~df["is_system"]]
    grouped = (
        real.groupby("sender")
        .agg(
            messages=("body", "count"),
            media=("is_media", "sum"),
            avg_sentiment=("sentiment", "mean"),
        )
        .sort_values("messages", ascending=False)
    )
    return [
        {
            "name": name,
            "messages": int(row.messages),
            "media": int(row.media),
            "avg_sentiment": round(float(row.avg_sentiment), 4),
        }
        for name, row in grouped.iterrows()
    ]


def compute_sentiment(df):
    real = df[~df["is_system"]]
    bucket = pd.cut(
        real["sentiment"],
        bins=[-1.01, -0.05, 0.05, 1.01],
        labels=["negative", "neutral", "positive"],
    )
    fractions = bucket.value_counts(normalize=True)
    return {label: float(fractions.get(label, 0.0)) for label in ["positive", "neutral", "negative"]}


def compute_top_influencers(df):
    return df[~df["is_system"]]["sender"].value_counts().head(5).index.tolist()


def compute_frequency(df):
    real = df[~df["is_system"]].copy()
    iso = real["timestamp"].dt.isocalendar()
    real["year_week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)

    daily = real.groupby(real["timestamp"].dt.date).size()
    weekly = real.groupby("year_week").size()

    return {
        "daily": [{"date": d.isoformat(), "count": int(c)} for d, c in daily.items()],
        "weekly": [{"iso_week": w, "count": int(c)} for w, c in weekly.items()],
    }


def compute_spam_flags(df):
    """Per-sender sliding time-window burst detector.

    Flags a sender if BURST_MESSAGE_THRESHOLD or more of their messages
    land within any BURST_WINDOW_SECONDS window. `examples` are 0-based
    positional row indices into the full parsed DataFrame (there's no
    per-message PK to reference instead at this stage).
    """
    real = df[~df["is_system"]].sort_values("timestamp")
    flags = []
    for sender, group in real.groupby("sender"):
        positions = [df.index.get_loc(i) for i in group.index]
        timestamps = group["timestamp"].tolist()
        n = len(timestamps)
        window_start = 0
        flagged_positions = set()
        for window_end in range(n):
            while (timestamps[window_end] - timestamps[window_start]).total_seconds() > BURST_WINDOW_SECONDS:
                window_start += 1
            if window_end - window_start + 1 >= BURST_MESSAGE_THRESHOLD:
                flagged_positions.update(positions[window_start : window_end + 1])
        if flagged_positions:
            flags.append(
                {
                    "sender": sender,
                    "reason": "high_volume_burst",
                    "examples": sorted(flagged_positions),
                }
            )
    return flags


def analyze(file_obj):
    df = parse_export(file_obj)
    sentiment_analysis(df)
    return {
        "summary": compute_summary(df),
        "per_user": compute_per_user(df),
        "peak_hours": compute_peak_hours(df),
        "frequency": compute_frequency(df),
        "sentiment": compute_sentiment(df),
        "top_influencers": compute_top_influencers(df),
        "spam_flags": compute_spam_flags(df),
    }
