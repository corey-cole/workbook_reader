"""Utility to create registered versions of all forms in a workbook"""
from workbook import Workbook

import click


# Workbook needs to take an optional TOC argument.  Or does it?
@click.command
@click.option('--container', type=click.Path(exists=True), help='Workbook container.  Can be TIFF, archive, or directory')
def main(container):
    wip = Workbook(container=container, load_contents=True)

    # If there is no table of contents, then we can't do anything with the
    # workbook.

    #
    # Iterate over the pages.  Skip any where the form type is unknown or unreadable
    # Register the form (i.e. align/resize according to template) and dump the
    # resulting registered version out to disk.
    #
    for page in wip.get_pages():
        # I'm responsible for registering the page
        # Once the page is registered, add it back to the TOC
        pass

if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
