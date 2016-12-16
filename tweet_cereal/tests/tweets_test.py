import unittest.mock as mock

import tweet_cereal.tweets as tweets


def test_get_collection_tweets():
    mock_session = mock.MagicMock()
    mock_session.get().json.side_effect = [
        {'objects': {'tweets': {'12': {'text': 'a'},
                                '34': {'text': 'b'}}},
         'response': {'timeline': [{'tweet': {'id': '12', 'sort_index': 1}},
                                   {'tweet': {'id': '34', 'sort_index': 2}}],
                      'position': {'was_truncated': True, 'min_position': 3}}},
        {'objects': {'tweets': {'56': {'text': 'd'},
                                '78': {'text': 'c'}}},
         'response': {'timeline': [{'tweet': {'id': '56', 'sort_index': 2}},
                                   {'tweet': {'id': '78', 'sort_index': 1}}],
                      'position': {'was_truncated': False, 'min_position': 3}}}
    ]

    result = tweets.get_collection_tweets(mock_session, 'id')
    assert list(result) == [['a', 'b'], ['c', 'd']]

    expected_url = 'https://api.twitter.com/1.1/collections/entries.json'
    expected_calls = [
        mock.call(expected_url, params={'id': 'id', 'count': 200}),
        mock.call(expected_url, params={
            'id': 'id', 'max_position': 3, 'count': 200}),
    ]
    for call in expected_calls:
        assert call in mock_session.get.mock_calls
