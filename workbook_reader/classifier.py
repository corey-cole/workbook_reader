"""Classify a collection of workboo page scans"""
from workbook import Workbook

import click

#
# While the long term goal is to use ML to inspect individual scans to
# determine form type/revision, we can use an OG (human) neural network
# to accomplish the task initially
#
@click.command()
@click.option('--container', type=click.Path(exists=True), help='Workbook container.  Can be TIFF, archive, or directory')
@click.option('--load-contents', is_flag=True)
@click.option('--debug', is_flag=True)
def main(container, load_contents, debug):
    # We can work with an existing TOC if one already exists
    # TODO: Workbook needs to have (and maybe take) a working directory for exploding TIFF/archive containers
    wip = Workbook(container=container, load_contents=load_contents)

    for page in wip.get_pages():
        # Show page on screen w/ dropdown
        # Do we allow users to include free-form text?
        pass

    # TODO: Should Workbook have an 'autosave' option that saves after each operation?
    wip.save_toc()


if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
