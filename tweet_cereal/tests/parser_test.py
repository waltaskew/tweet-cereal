import tweet_cereal.parser as parser


def test_parse_empty():
    assert parser.parse('') == []


def test_parse_text():
    assert parser.parse('abc def') == [
        parser.Text('abc def')]


def test_parse_text_with_breaks():
    assert parser.parse('abc #par def #break ghi jkl') == [
        parser.Text('abc'),
        parser.NewParagraph(),
        parser.Text('def'),
        parser.Break(),
        parser.Text('ghi jkl'),
    ]


def test_parse_new_chapters():
    assert parser.parse('#newch') == [parser.NewChapter('')]


def test_parse_new_chapters_with_text():
    assert parser.parse('#newch abc def') == [
        parser.NewChapter('abc def')]


def test_parse_all_the_things():
    assert (
        parser.parse('#newch #break abc #newch ghi #break jkl #par') == [
            parser.NewChapter(''),
            parser.Break(),
            parser.Text('abc'),
            parser.NewChapter('ghi'),
            parser.Break(),
            parser.Text('jkl'),
            parser.NewParagraph(),
        ]
    )
