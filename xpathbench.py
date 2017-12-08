#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import partial
from timeit import default_timer as timer

from scrapy.http import HtmlResponse
from scrapy.utils.response import get_base_url
import click

from bench_utils import extract_file_from_tar


def bench_xpath(filename):
    """ Benchmark the link extraction """
    total = 0
    time = 0
    for f in extract_file_from_tar(filename):
        html = f.read()

        response = HtmlResponse(url="local", body=html, encoding='utf8')

        start = timer()

        rating = response.xpath(
            "//*[@id='content_inner']/article/div[1]/div[2]/p[3]/i[1]").extract(),  # .split(' ')[-1],
        title = response.xpath(
            "//*[@id=('content_inner')]/article/div[1]/div[2]/h1").extract(),
        price = response.xpath(
            "//*[@id=('content_inner')]/article/div[1]/div[2]/p[1]"),
        stock = ''.join(response.xpath(
            "//*[@id=('content_inner')]/article/div[1]/div[2]/p[2]").re('(\d+)')),

        end = timer()
        page = [rating, title, price, stock]

        total = total + 1
        time = time + end - start

    click.echo("Total number of pages extracted = {0}".format(total))
    click.echo("Time taken = {0}".format(time))
    click.secho("Rate of link extraction : {0} pages/second\n".format(
        float(total / time)))

    with open("Benchmark.txt", 'w') as g:
        g.write(" {0}".format((float(total / time))))


def bench_get_base_url(filename, html_already_parsed=False):
    """ Benchmark the extraction of the base url using xpath """
    click.secho('HTML is already parsed = {!r}'.format(html_already_parsed))
    time = 0
    num_of_files = 0

    for fd in extract_file_from_tar(filename):
        num_of_files += 1
        html = fd.read()

        if not html_already_parsed:
            start = timer()
            response = HtmlResponse(url="local", body=html, encoding='utf8')
        else:
            response = HtmlResponse(url="local", body=html, encoding='utf8')
            start = timer()

        response.xpath('.//base').extract()

        end = timer()
        time = time + (end - start)

    click.secho('Total parsed files = {}'.format(num_of_files))
    click.secho('Time taken: {}\n'.format(time))


def bench_current_get_base_url_implementation(filename):
    """ Benchmark the current implementation of get_base_url in
    scrapy.utils.response.get_base_url """
    time = 0
    num_of_files = 0

    for fd in extract_file_from_tar(filename):
        num_of_files += 1
        html = fd.read()

        start = timer()

        response = HtmlResponse(url="local", body=html, encoding='utf8')
        get_base_url(response)

        end = timer()
        time = time + (end - start)

    click.secho('Total parsed files = {}'.format(num_of_files))
    click.secho('Time taken: {}\n'.format(time))


def bench_get_base_html_parsed(filename):
    """ Benchmark the get_base_url function when the HTML is already
    parsed """
    return bench_get_base_url(filename, html_already_parsed=True)


@click.command()
@click.option('--filename', default='bookfiles.tar.gz',
              help='Filename of the .tar.gz file containg html'
                   'files to use in the benchmark')
@click.option('--run-only', default='', help='Run only the benchmark function')
def main(filename, run_only):
    click.secho('Using {} to run the benchmark\n'.format(filename), fg='green')
    benchmark_functions = [
        bench_xpath,
        bench_get_base_url,
        bench_get_base_html_parsed,
        bench_current_get_base_url_implementation, ]

    if run_only:
        benchmark_functions = filter(lambda x: x.__name__ == run_only,
                                     benchmark_functions)

    for f in benchmark_functions:
        click.secho(f.__doc__.lstrip() + '\n', fg='white', bold=True)
        f(filename)


if __name__ == "__main__":
    main()
