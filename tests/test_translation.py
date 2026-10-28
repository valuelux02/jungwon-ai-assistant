import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import app
import sllm_engine as engine


class TranslationTests(unittest.TestCase):
    def setUp(self):
        engine._TRANSLATION_CACHE.clear()
        self.client = app.app.test_client()

    def test_information_file_and_language_pages(self):
        info = self.client.get('/api/sllm-info')
        self.assertEqual(info.status_code, 200)
        self.assertEqual(set(info.json['supported_languages']), set(engine.SUPPORTED_LANGUAGES))
        for lang in engine.SUPPORTED_LANGUAGES:
            with self.subTest(lang=lang):
                page = self.client.get('/?tab=translate&lang=' + lang)
                self.assertEqual(page.status_code, 200)
                self.assertIn(b'value="km"', page.data)
                self.assertIn(b'/api/sllm-info', page.data)

    def test_all_language_pairs_use_local_glossary(self):
        terms = {'ko': '장학금', **engine.ACADEMIC_TERMS['장학금']}
        with patch.object(engine, '_query_google', side_effect=AssertionError('Network not needed')):
            for source, original in terms.items():
                for target, expected in terms.items():
                    with self.subTest(source=source, target=target):
                        response = self.client.post('/api/translate', json={
                            'text': original, 'source_lang': source, 'target_lang': target
                        })
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(response.json['translated'], expected)

    def test_auto_detection_is_forwarded_and_short_translation_accepted(self):
        with patch.object(engine, '_query_google', return_value='Hi') as google:
            response = self.client.post('/api/translate', json={
                'text': 'Xin chào', 'source_lang': 'auto', 'target_lang': 'en'
            })
        self.assertEqual(response.json['translated'], 'Hi')
        google.assert_called_once_with('Xin chào', 'auto', 'en')

    def test_five_foreign_languages_reach_provider(self):
        for lang in ('vi', 'en', 'km', 'ne', 'uz'):
            with self.subTest(lang=lang), patch.object(engine, '_query_google', return_value='translated') as google:
                response = self.client.post('/api/translate', json={
                    'text': '행정실에 문의해 주세요.', 'source_lang': 'ko', 'target_lang': lang
                })
                self.assertEqual(response.status_code, 200)
                google.assert_called_once_with('행정실에 문의해 주세요.', 'ko', lang)

    def test_fallback_does_not_truncate_long_utf8_text(self):
        original = ''.join(f'문장{index:04d}' for index in range(250)) + '끝'
        sent = []

        def memory(url, timeout):
            query = parse_qs(urlparse(url).query)['q'][0]
            sent.append(query)
            self.assertLessEqual(len(query.encode('utf-8')), 350)
            return {'responseStatus': 200, 'responseData': {'translatedText': 'translated'}}

        with patch.object(engine, '_query_google', return_value=None), patch.object(engine, '_http_get_json', side_effect=memory):
            result = engine.translate_text(original, 'en', 'ko', strict=True)
        self.assertTrue(result)
        self.assertEqual(''.join(sent), original)

    def test_shorter_text_also_fits_fallback_byte_limit(self):
        original = '가' * 180
        chunks = []

        def memory(url, timeout):
            query = parse_qs(urlparse(url).query)['q'][0]
            chunks.append(query)
            self.assertLessEqual(len(query.encode('utf-8')), 350)
            return {'responseStatus': 200, 'responseData': {'translatedText': 'translated'}}

        with patch.object(engine, '_query_google', return_value=None), patch.object(engine, '_http_get_json', side_effect=memory):
            engine.translate_text(original, 'en', 'ko', strict=True)
        self.assertEqual(''.join(chunks), original)

    def test_auto_failure_returns_503_and_can_retry(self):
        payload = {'text': 'Example sentence', 'source_lang': 'auto', 'target_lang': 'vi'}
        with patch.object(engine, '_query_google', return_value=None), patch.object(engine, '_http_get_json') as memory:
            self.assertEqual(self.client.post('/api/translate', json=payload).status_code, 503)
            memory.assert_not_called()
        self.assertFalse(engine._TRANSLATION_CACHE)
        with patch.object(engine, '_query_google', return_value='Xin chào'):
            response = self.client.post('/api/translate', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_provider_error_is_not_presented_as_translation(self):
        with patch.object(engine, '_query_google', return_value=None), patch.object(engine, '_http_get_json', return_value={
            'responseStatus': 429, 'responseData': {'translatedText': 'QUOTA EXCEEDED'}
        }):
            response = self.client.post('/api/translate', json={
                'text': 'Example sentence', 'source_lang': 'en', 'target_lang': 'km'
            })
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json['translated'], '')

    def test_invalid_payloads(self):
        for payload in ([], {}, {'text': 42}, {'text': 'hello', 'target_lang': None},
                        {'text': 'hello', 'source_lang': 'xx'}, {'text': 'hello', 'target_lang': 'xx'},
                        {'text': 'a' * 10001}):
            with self.subTest(payload=str(payload)[:80]):
                self.assertEqual(self.client.post('/api/translate', json=payload).status_code, 400)

    def test_khmer_chat_retrieval_and_translated_reply(self):
        with patch.object(engine, '_query_google', return_value='អាហារូបករណ៍'):
            response = self.client.post('/api/chat', json={'message': 'អាហារូបករណ៍', 'lang': 'km'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['intent'], '장학금')
        self.assertEqual(response.json['lang'], 'km')
        self.assertTrue(response.json['korean_text'])

    def test_chat_falls_back_to_korean_with_failure_notice(self):
        with patch.object(engine, '_query_google', return_value=None), patch.object(engine, '_http_get_json', return_value=None):
            response = self.client.post('/api/chat', json={'message': '장학금', 'lang': 'km'})
        self.assertEqual(response.json['reply'], response.json['korean_text'])
        self.assertEqual(response.json['lang'], 'ko')
        self.assertIn('연결 실패', response.json['sources'][-1])

    def test_direct_translation_chat_reports_failure(self):
        with patch.object(engine, '_query_google', return_value=None):
            response = self.client.post('/api/chat', json={'message': 'translate: Hello there', 'lang': 'km'})
        self.assertEqual(response.json['intent'], 'translation_error')


if __name__ == '__main__':
    unittest.main()
