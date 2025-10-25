import pytest
from bs_config import Env

from twittergram.config import RssConfig, RssOrder


@pytest.mark.parametrize(
    "value,order",
    [
        ("chronological", RssOrder.CHRONOLOGICAL),
        ("reverse_chronological", RssOrder.REVERSE_CHRONOLOGICAL),
    ],
)
def test_rss_config(value, order):
    env = Env.load_from_dict({"FEED_URL": "https://example.org", "ORDER": value})
    config = RssConfig.from_env(env)
    assert config
    assert config.order == order
