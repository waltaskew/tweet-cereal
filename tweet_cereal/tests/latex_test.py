import tweet_cereal.latex as latex
import tweet_cereal.parser as parser


def test_to_latex_text():
    assert latex.to_latex(parser.Text('hey $ ~snakes~')) == (
        'hey \\$ \\textasciitilde{}snakes\\textasciitilde{}\n'
    )


def test_to_latex_chapter():
    assert latex.to_latex(parser.NewChapter('$snakes__')) == (
        '\\chapter{\\$snakes\\_\\_}\n'
    )
    assert latex.to_latex(parser.NewChapter('')) == '\\chapter{}\n'


def test_to_latex_paragraph():
    assert latex.to_latex(parser.NewParagraph()) == '\n'


def test_to_latex_break():
    assert latex.to_latex(parser.Break()) == "\\starbreak{}\n"
