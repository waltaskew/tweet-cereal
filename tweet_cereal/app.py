"""Define an app for processing requests to LaTeX up tweets."""

import base64
import os

import flask
import flask_socketio
import eventlet
import redis

import tweet_cereal.tasks as tasks
import tweet_cereal.tweets as tweets

JOB_RESULT_POLL_INTERVAL = 1

app = flask.Flask(__name__)
socketio = flask_socketio.SocketIO(app, binary=True, async_mode='eventlet')
redis_conn = redis.from_url(os.environ['REDIS_URL'])


@socketio.on('render')
def render_pdf(message):
    """Render PDFs for the requested twitter collection.

    Parameters
    ----------
    message : dict
        Description of the timeline to render.

    Returns
    -------
    bytes
        The PDF representing the collection.
    """
    session = tweets.get_oauth_session(
        os.environ['TWITTER_CONSUMER_KEY'],
        os.environ['TWITTER_CONSUMER_SECRET'],
        os.environ['TWITTER_ACCESS_TOKEN'],
        os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    )

    job = tasks.write_pdf_from_timeline.delay(
        session, message['collection_id'])
    while not job.ready():
        # While we poll the job to completion, sleep to yield the event loop.
        eventlet.sleep(JOB_RESULT_POLL_INTERVAL)

    result = job.result
    # Drop the result from Redis now that we've read it.
    # This is hacky -- the proper way to do this is to set
    # the celery result_expires timeout to a reasonable value
    # so the job results don't hang around too long.
    # However, we're doing things on the cheap and free-tier
    # Redis in Heroku is just 25 MB, so we need to clear the result now.
    #
    # The really proper way to do this is to use S3 rather than Redis
    # to pass PDFs back from the workers but again, we're on the cheap.
    redis_conn.delete('celery-task-meta-%s' % job.task_id)
    return result
