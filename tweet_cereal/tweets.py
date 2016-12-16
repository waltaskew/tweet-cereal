"""Functions for working with the Twitter API."""

import requests_oauthlib


def get_oauth_session(consumer_key, consumer_secret,
                      access_token, access_token_secret):
    """Builds an OAuth session to Twitter with the given secrets.

    Parameters
    ----------
    consumer_key : str
    consumer_secret : str
    access_token : str
    access_token_secret : str

    Returns
    -------
    requests_oauthlib.OAuth1Session
    """
    session = requests_oauthlib.OAuth1Session(
         client_key=consumer_key,
         client_secret=consumer_secret,
         resource_owner_key=access_token,
         resource_owner_secret=access_token_secret,
     )
    session.headers = {'User-Agent': 'Tweet Cereal'}
    return session


def get_collection_tweets(session, collection_id):
    """Collects tweet content for the given collection.

    Parameters
    ----------
    session : requests_oauthlib.OAuth1Session
        OAuth session to use when making requests against the twitter api.
    collection_id : str
        ID of the collection from which to return tweets.

    Raises
    ------
    requests.exceptions.HTTPError
        If a request to the Twitter API fails.

    Yields
    ------
    [str]
        Content of the tweets. The tweets are returned in batches of 200.
    """
    max_position = None
    while True:
        params = {'id': collection_id, 'count': 200}
        if max_position is not None:
            params['max_position'] = max_position

        resp = session.get(
            'https://api.twitter.com/1.1/collections/entries.json',
            params=params,
        )
        resp.raise_for_status()

        # The tweets are returned as a {tweet_id: tweet} mapping.
        # The order of the tweets in the collection is defined
        # by the 'response' section of the response.
        data = resp.json()
        ordering = data['response']['timeline']
        ordering.sort(key=lambda order: order['tweet']['sort_index'])
        yield [data['objects']['tweets'][order['tweet']['id']]['text']
               for order in ordering]

        # The was_truncated field indicates whether we need to make
        # additional requests to retrieve more tweets in the collection.
        # The 'min_position' of this response becomes the 'max_position'
        # of the next request.
        if data['response']['position']['was_truncated']:
            max_position = data['response']['position']['min_position']
        else:
            return
