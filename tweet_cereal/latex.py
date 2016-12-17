"""Functions for writing parsed tweets as LaTeX."""

import functools
import tempfile

import tweet_cereal.parser as parser

ESCAPE_CHARS = {
      '\\': "\\textbackslash{}",
      '^': "\\textasciicircum{}",
      '~': "\\textasciitilde{}",
}
ESCAPE_CHARS.update({char: "\\%s" % char for char in "#$%&_{}"})


def write_latex(title, author, parsed_tweets):
    """Writes the LaTeX for the parsed tweet to disk.

    Parameters
    ----------
    title : str
        Title of the document.
    author : str
        Author of the document.
    parsed_tweets : [[Text | NewChapter | NewParagraph | Break]]
        A sequence of parsed tweets as returned from a parser.parse call.

    Returns
    -------
    str
        The location of the written LaTeX document.
    """
    with tempfile.NamedTemporaryFile('w', suffix='.tex', delete=False) as out:
        out.write(intro_latex(title, author))
        for parse in parsed_tweets:
            out.writelines(to_latex(lexeme) for lexeme in parse)
        out.write(outro_latex())
        return out.name


@functools.singledispatch
def to_latex(lexeme):
    """"Returns the LaTeX representation of the given lexeme.

    This is the dispatch method which is implemented below
    for each type of lexeme.

    Parameters
    ----------
    Text | NewChapter | NewParagraph | Break
        The parsed lexeme to render as LaTeX.

    Returns
    -------
    str
        The LaTex representation of the lexeme.
    """
    raise NotImplementedError


@to_latex.register(parser.Text)
def render_text(lexeme):
    """Renders LaTeX escaped text."""
    return escape_latex(lexeme.text) + '\n'


@to_latex.register(parser.NewChapter)
def render_new_chapter(lexeme):
    """Renders a chapter command."""
    return "\\chapter{%s}\n" % escape_latex(lexeme.text)


@to_latex.register(parser.NewParagraph)
def render_new_paragraph(lexeme):
    """Renders a newline."""
    return '\n'


@to_latex.register(parser.Break)
def render_break(lexeme):
    """Renders a starbreak command defined in the intro_latex function."""
    return "\\starbreak{}\n"


def intro_latex(title, author):
    """Provides the beginning of the LaTeX document.

    Parameters
    ----------
    title : str
        Title of the document.
    author : str
        Author of the document.

    Returns
    -------
    str
        The document's beginning.
    """
    return """
\\documentclass[12pt,oneside]{memoir}
\\newcommand{\\starbreak}{
  \\plainbreak{1}
  \\fancybreak{* * *}
  \\plainbreak{1}
}
\\title{%s}
\\author{%s}
\\begin{document}
\\maketitle

""" % (escape_latex(title), escape_latex(author))


def outro_latex():
    """Provides the end of the LaTeX document.

    Returns
    -------
    str
        The end of the document.
    """
    return "\n\\end{document}\n"


def escape_latex(text):
    """Add escape sequences for special LaTeX characters.

    Parameters
    ----------
    text : str
        Text to be escaped.

    Returns
    -------
    str
        The escaped text.
    """
    return ''.join(ESCAPE_CHARS.get(char, char) for char in text)
