
"""Unit tests for TMDB parsing logic (no network, no real key)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from modules.api import tmdb_api


class TestTrailerPick(unittest.TestCase):
    def test_prefers_official_trailer(self):
        details = {
            "videos": {
                "results": [
                    {"site": "YouTube", "type": "Teaser", "key": "TEASER"},
                    {"site": "YouTube", "type": "Trailer", "key": "TRAILER"},
                    {"site": "Vimeo", "type": "Trailer", "key": "V"},
                ]
            }
        }
        self.assertEqual(tmdb_api.pick_trailer(details), "TRAILER")

    def test_returns_none_when_no_youtube(self):
        details = {"videos": {"results": [
            {"site": "Vimeo", "type": "Trailer", "key": "V"}
        ]}}
        self.assertIsNone(tmdb_api.pick_trailer(details))

    def test_returns_none_when_videos_missing(self):
        self.assertIsNone(tmdb_api.pick_trailer({}))


class TestImageUrl(unittest.TestCase):
    def test_builds_url(self):
        url = tmdb_api.image_url("/abc.jpg", "w500")
        self.assertTrue(url.endswith("/w500/abc.jpg"))

    def test_none_path(self):
        self.assertIsNone(tmdb_api.image_url(None))


class TestFetchErrors(unittest.TestCase):
    def test_missing_token_raises(self):
        with patch.object(tmdb_api, "has_tmdb_token", return_value=False):
            with self.assertRaises(tmdb_api.TMDBError):
                tmdb_api.get_popular("movie")

    def test_popular_parses_results(self):
        fake = {"results": [{"id": 1, "title": "X"}]}
        with patch.object(tmdb_api, "has_tmdb_token", return_value=True), \
             patch.object(tmdb_api, "_get", return_value=fake):
            self.assertEqual(tmdb_api.get_popular("movie")[0]["id"], 1)


if __name__ == "__main__":
    unittest.main()