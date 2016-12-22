"""Celery configuration and tasks for generating PDFs."""

import glob
import multiprocessing
import os
import shutil
import subprocess
import tempfile

import celery

import tweet_cereal.latex as latex
import tweet_cereal.parser as parser
import tweet_cereal.tweets as tweets

app = celery.Celery(__name__)
app.conf.update(
    broker_url=os.environ['REDIS_URL'],
    result_backend=os.environ['REDIS_URL'],
    task_acks_late=True,
    event_serializer='pickle',
    result_serializer='pickle',
    task_serializer='pickle',
    accept_content=('pickle',),
    worker_concurrency=multiprocessing.cpu_count() * 4,
)


@app.task
def write_pdf_from_timeline(session, collection_id):
    """Create a PDF for the collection and return its contents.

    Parameters
    ----------
    session : requests_oauthlib.OAuth1Session
        Session to use when reading the timeline.
    collection_id : str
        ID of the collection for which to build a PDF.

    Returns
    -------
    bytes
        The PDF generated fromt the collection.
    """
    collection = tweets.get_collection_tweets(session, collection_id)
    parsed_tweets = (parser.parse(tweet)
                     for batch in collection
                     for tweet in batch)
    tex_file = latex.write_latex(
        'A Tale of Two Cities', 'Chucky D', parsed_tweets)

    pdf_dir = tempfile.mkdtemp()
    subprocess.check_call(('pdflatex', '-output-directory', pdf_dir, tex_file))
    pdf = glob.glob('%s/*.pdf' % pdf_dir)[0]

    with open(pdf, 'rb') as pdf_file:
        contents = pdf_file.read()
    os.remove(tex_file)
    shutil.rmtree(pdf_dir)

    return contents
