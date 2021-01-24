#!/usr/bin/python3

from config import get_scraper


def main():
    scraper = get_scraper()
    grades = scraper.request_grade()

    print('\n'.join([
        scraper.fmt_grades(grades),
        scraper.fmt_gpa(grades, by_year=True),
    ]))


if __name__ == "__main__":
    main()
