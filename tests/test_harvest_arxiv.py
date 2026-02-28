import unittest
from unittest.mock import patch, MagicMock
import feedparser
import src.harvest_arxiv as ha

class TestHarvestArxiv(unittest.TestCase):
    def setUp(self):
        # Construct a minimal Atom feed string
        self.feed_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1234.5678v1</id>
    <title>Sample Paper Title</title>
    <summary>Abstract text here.</summary>
    <author><name>First Author</name></author>
    <author><name>Second Author</name></author>
    <published>2023-01-01T00:00:00Z</published>
    <updated>2023-01-02T00:00:00Z</updated>
    <link href="http://arxiv.org/pdf/1234.5678v1.pdf" type="application/pdf"/>
  </entry>
</feed>
'''
        self.parsed = feedparser.parse(self.feed_xml)

    @patch('src.harvest_arxiv.requests.get')
    def test_harvest_arxiv(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = self.feed_xml
        result = ha.harvest_arxiv('1234.5678')
        self.assertEqual(result['id'], '1234.5678')
        self.assertEqual(result['title'], 'Sample Paper Title')
        self.assertIn('First Author', result['authors'])
        self.assertEqual(result['summary'], 'Abstract text here.')
        self.assertEqual(result['published'], '2023-01-01T00:00:00Z')
        self.assertEqual(result['updated'], '2023-01-02T00:00:00Z')
        self.assertTrue(result['pdf_url'].endswith('.pdf'))

if __name__ == '__main__':
    unittest.main()
