import click

from movie_collection_etl.setup_database import create_database_engine
from movie_collection_etl.web_crawler import web_crawler

@click.command()
@click.option('--setupdb', is_flag=True, default=False, help='Flag for setting up the database.')
@click.option('--crawl', is_flag=True, default=False, help='Flag for crawling the web.')
def main(setupdb, crawl):
    """Simple package for setting up database for movie collection
        and using the web crawling to fill collection detialsls
    """
    if setupdb:
        create_database_engine()
    
    if crawl:
        web_crawler()
    
    if not (setupdb or crawl):
        click.echo('Either select setupdb to setup database or crawl for web scrapping')


if __name__ == '__main__':
    main()