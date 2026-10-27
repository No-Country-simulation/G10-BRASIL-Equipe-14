import unittest
from unittest.mock import patch, MagicMock
from src.pipeline.sample_collector import DataSourceCollector


class TestDataSourceCollector(unittest.TestCase):

    @patch("src.pipeline.sample_collector.requests.Session.get")
    def test_fetch_stack_exchange_raw(self, mock_get):
        # Mock da resposta bruta da API do Stack Exchange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "question_id": 123456,
                    "title": "Teste de Pergunta Stack Exchange",
                    "body": "<p>Conteúdo de teste</p>",
                    "link": "https://stackoverflow.com/q/123456",
                    "creation_date": 1711929600,
                    "score": 10,
                }
            ],
            "has_more": False,
        }
        mock_get.return_value = mock_response

        collector = DataSourceCollector()
        data = collector.fetch_stack_exchange(tag="artificial-intelligence", limit=1)

        # Valida se o payload bruto foi retornado corretamente
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["question_id"], 123456)
        self.assertEqual(data["items"][0]["title"], "Teste de Pergunta Stack Exchange")

    @patch("src.pipeline.sample_collector.requests.Session.get")
    def test_fetch_hacker_news_raw(self, mock_get):
        # Mock da resposta bruta da Algolia API (Hacker News)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "hits": [
                {
                    "objectID": "987654",
                    "title": "Show HN: Python Pipeline",
                    "url": "https://news.ycombinator.com/item?id=987654",
                    "points": 42,
                    "author": "dev_guru",
                }
            ],
            "nbHits": 1,
        }
        mock_get.return_value = mock_response

        collector = DataSourceCollector()
        data = collector.fetch_hacker_news(query="artificial-intelligence", limit=1)

        # Valida se o payload bruto foi retornado corretamente
        self.assertIn("hits", data)
        self.assertEqual(len(data["hits"]), 1)
        self.assertEqual(data["hits"][0]["objectID"], "987654")
        self.assertEqual(data["hits"][0]["author"], "dev_guru")

    @patch("src.pipeline.sample_collector.requests.Session.get")
    def test_fetch_mastodon_raw(self, mock_get):
        # Mock da resposta bruta da timeline do Mastodon
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "11223344",
                "content": "<p>Testando a API do Mastodon com Python #python</p>",
                "created_at": "2026-03-30T12:00:00.000Z",
                "account": {"id": "555", "username": "mastodon_user"},
            }
        ]
        mock_get.return_value = mock_response

        collector = DataSourceCollector()
        data = collector.fetch_mastodon(
            instance="mastodon.social", hashtag="artificial-intelligence", limit=1
        )

        # Valida se a lista bruta de posts foi retornada corretamente
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "11223344")
        self.assertEqual(data[0]["account"]["username"], "mastodon_user")


if __name__ == "__main__":
    unittest.main()
