"""Functions for parsing tweets and out-putting LaTeX."""

import collections
import re

import parsec


# The targets of our parsing.
# We look for instructions to insert text, chapters,
# paragraphs and line breaks.
Text = collections.namedtuple('Text', ['text'])
NewChapter = collections.namedtuple('NewChapter', ['text'])
NewParagraph = collections.namedtuple('NewParagraph', [])
Break = collections.namedtuple('Break', [])

# Parse and ignore trailing white space after our reserved words.
whitespace = parsec.regex(r'\s*', re.MULTILINE)
skip_whitespace = lambda p: p << whitespace  # noqa

# Break and new paragraph commands are simply reserved words.
break_command = skip_whitespace(parsec.string('#break')).result(Break())
par_command = skip_whitespace(parsec.string('#par')).result(NewParagraph())

# The newch_parser is used to implement the newch_command parser below.
newch_parser = skip_whitespace(parsec.string('#newch'))
# The text parser consumes all input between reserved words.
commands = '#newch|#par|#break'
text_parser = parsec.regex('(?!(%s))(.+?)(?=%s|$)' % (commands, commands))

@parsec.Parser
def text_command(text, index):
    """Parse a text command returning the text to be inserted."""
    res = text_parser(text, index)
    if not res.status:
        return res
    else:
        return parsec.Value.success(res.index, Text(res.value.strip()))

@parsec.Parser
def newch_command(text, index):
    """Parse a new chapter command, which optionally may contain a title."""
    is_chapter = newch_parser(text, index)
    if not is_chapter.status:
        return is_chapter
    else:
        chapter_text = text_parser(text, is_chapter.index)
        if not chapter_text.status:
            return parsec.Value.success(is_chapter.index, NewChapter(''))
        else:
            return parsec.Value.success(
                chapter_text.index, NewChapter(chapter_text.value.strip()))


tweet_parser = parsec.many(
    par_command ^ break_command ^ newch_command ^ text_command)


def parse(text):
    """Parse formatting commands from the given text.

    Parameters
    ----------
    text : str
        Body of the tweet to be parsed.

    Returns
    -------
    [Text | NewChapter | NewParagraph | Break]
        A list of Text, NewChapter, NewParagraph and Break objects
        representing the sequence of formatting commands in the tweet.
    """
    return tweet_parser.parse(text)
