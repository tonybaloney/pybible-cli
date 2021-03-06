import argparse
import sys
from pybible import pybible_load
from collections import namedtuple

Reference = namedtuple("Reference", ["verse_text", 'book_title', 'chapter_number', 'verse_number'])


def configure_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Bible reference', epilog="\u271e")
    parser.add_argument("--bible", metavar="BIBLE", help="Bible version to use", choices=["kj"], default="kj")

    reference_group = parser.add_mutually_exclusive_group()
    reference_group.add_argument("-ot", "--old_testament", help="Reference the old testament",
                                 action="store_true")
    reference_group.add_argument("-nt", "--new_testament", help="Reference the new testament",
                                 action="store_true")
    reference_group.add_argument("--book", metavar="BOOK_NAME", help="Reference book")
    reference_group.add_argument("--chapter", metavar=("BOOK_NAME", "CHAPTER_NUMBER"),
                                 help="Reference book and chapter", nargs=2)
    reference_group.add_argument("--verse", metavar=("BOOK_NAME", "CHAPTER_NUMBER", "VERSE_NUMBER"),
                                 help="Reference book, chapter and verse", nargs=3)
    parser.add_argument("-r", "--reference", help="Include book, chapter number and verse reference",
                        action="store_true")
    parser.add_argument("-s", "--size", help="Size of bible, book, chapter or vere referenced", action="store_true")
    return parser


def process_arguments(parser: argparse.ArgumentParser):
    args = parser.parse_args()
    bible_arg = args.bible

    bible = pybible_load.load(bible_arg)

    if args.old_testament:
        if args.size:
            return f"The old testament has {len(bible.ot())} books"
        else:
            references = [Reference(verse.text, book.title, chapter.number, verse.number) for book in bible.ot()
                          for chapter in book.chapters for verse in chapter.verses]

    elif args.new_testament:
        if args.size:
            return f"The new testament has {len(bible.nt())} books"
        else:
            references = [Reference(verse.text, book.title, chapter.number, verse.number) for book in bible.nt()
                          for chapter in book.chapters for verse in chapter.verses]

    elif args.book:
        book = bible[args.book]
        if args.size:
            return f"{book.title} has {len(book)} chapters"
        else:
            references = [Reference(verse.text, book.title, chapter.number, verse.number)
                          for chapter in book.chapters for verse in chapter.verses]

    elif args.chapter:
        book = bible[args.chapter[0]]
        chapter = book[cast_integer_argument(parser, args.chapter[1], "--chapter", "CHAPTER_NUMBER")]
        if args.size:
            return f"Chapter {chapter.number} of {book.title} has {len(chapter)} verses"
        else:
            references = [Reference(verse.text, book.title, chapter.number, verse.number) for verse in chapter.verses]

    elif args.verse:
        book = bible[args.verse[0]]
        chapter = book[cast_integer_argument(parser, args.verse[1], "--verse", "CHAPTER_NUMBER")]
        verse = chapter[cast_integer_argument(parser, args.verse[2], "--verse", "VERSE_NUMBER")]
        if args.size:
            return f"Verse {verse.number} of Chapter {chapter.number} of {book.title} has {len(verse)} characters"
        else:
            references = [Reference(verse.text, book.title, chapter.number, verse.number)]

    else:
        if args.size:
            return f"{bible.name} has {len(bible)} books"
        else:
            references = [Reference(verse.text, book.title, chapter.number, verse.number) for book in bible.books
                          for chapter in book.chapters for verse in chapter.verses]

    if args.reference:
        return [f"{reference.verse_text} - {reference.book_title} {reference.chapter_number}:{reference.verse_number}"
                for reference in references]
    else:
        return [f"{reference.verse_text}" for reference in references]


def cast_integer_argument(my_parser: argparse.ArgumentParser, argument: str, argument_name: str,
                          argument_metavar: str) -> int:
    try:
        position_one_based_numbered = int(argument) - 1
        if position_one_based_numbered < 0:
            raise argparse.ArgumentTypeError()
        return position_one_based_numbered
    except (argparse.ArgumentTypeError, ValueError):
        my_parser.print_usage()
        print(f"{my_parser.prog}: error: argument {argument_name}: {argument_metavar} must be an integer number "
              f"greater then 0")
        sys.exit(2)


def print_command_response(response):
    if isinstance(response, list):
        for verse in response:
            print(verse)
    else:
        print(response)


def main():
    parser = configure_arg_parser()
    response = process_arguments(parser)
    print_command_response(response)


if __name__ == "__main__":
    main()
