#!/usr/bin/python3

from scrapers import Scraper


def main():
    scraper = Scraper()
    grades = scraper.request_grade()

    print('\n'.join([
        scraper.fmt_grades(grades),
        scraper.fmt_gpa(grades, by_year=True),
    ]))


if __name__ == "__main__":
    main()
