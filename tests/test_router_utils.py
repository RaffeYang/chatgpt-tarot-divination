import unittest

from src.chatgpt_router import _normalize_openai_base_url, _resolve_provider


class RouterUtilsTest(unittest.TestCase):

    def test_openai_base_url_auto_append_v1(self):
        self.assertEqual(
            _normalize_openai_base_url("https://api.openai.com"),
            "https://api.openai.com/v1",
        )

    def test_anthropic_base_url_keep_original(self):
        self.assertEqual(
            _normalize_openai_base_url("https://api.minimaxi.com/anthropic"),
            "https://api.minimaxi.com/anthropic",
        )

    def test_resolve_provider_with_explicit_protocol(self):
        self.assertEqual(
            _resolve_provider("anthropic", "https://proxy.example.com", "gpt-4o-mini"),
            "anthropic",
        )
        self.assertEqual(
            _resolve_provider("openai", "https://api.minimaxi.com/anthropic", "MiniMax-M2.5"),
            "openai",
        )

    def test_resolve_provider_by_model_and_base(self):
        self.assertEqual(
            _resolve_provider(None, "https://api.minimaxi.com/gateway", "MiniMax-M2.5"),
            "anthropic",
        )
        self.assertEqual(
            _resolve_provider(None, "https://api.openai.com/v1", "gpt-4o-mini"),
            "openai",
        )


if __name__ == "__main__":
    unittest.main()
