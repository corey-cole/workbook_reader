"""Class representing a filled out workbook scan"""
import os
import sqlite3

# Version information and any other global properties that apply.
# While I would generally expect a workbook to contain pages that are all the same edition
# I can also easily imagine a scenario where it does not:  Running out of pages and falling back to
# another older set, or observer being accidentally provided with mixed pages.
# As such, each page needs to record it's own type & edition.
# That's also why we're not recording workbook data here.
METADATA_SCHEMA_STMT = """
CREATE TABLE tubs_metadata (tubs_version integer, last_saved text)
""".strip()

# Filename needs to include internal location for archives/TIFF files
# Probably want to use something like 'workbook.tiff:1'
PAGES_SCHEMA_STMT = """
CREATE TABLE wb_pages (
    filename text,
    page_number integer,
    form_type text,
    registered_filename text,
    comments text,
    excluded text
)
""".strip()

# Increment this when making a breaking change to TOC schemas
TUBS_VERSION = 1
TOC_FILENAME = 'toc.db'


class Workbook:
    """
    Workbook is our interface to a container holding a collection of images.
    """
    # TODO: How much recursion do we support?  Flat directory, nested directory, zip of zips, multiple TIFF files in a directory, etc.?
    def __init__(self, container=None, load_contents=False, properties=None):
        if not load_contents:
            self.table_of_contents = sqlite3.connect(':memory:')
            Workbook.initialize_schema(self.table_of_contents)
        else:
            # Load an existing file, failing if we cannot
            toc_file = Workbook.find_toc_file(container)
            if not toc_file:
                raise f"No table of contents found for container {container}"
            # TODO: Validate schema
            # TODO: How do we rationalize this file vs. toc.db?
            self.table_of_contents = sqlite3.connect(toc_file)
        self.container = container
        self.properties = properties or {}

    def add_registered_page(self, filename):
        # DB write to TOC, nothing more
        pass

    def get_pages(self, page_range=None, form_type=None):
        # This needs to be a generator rather than a concrete list
        return []

    # TODO: Need to initialize TOC if it's empty
    ## e.g. Iterate over directory or TIFF & fill in pages
    # TODO: Need to describe delta between recorded pages and container
    # TODO: Need to list unclassified pages
    # TODO: Need to list pages that haven't been registered

    @staticmethod
    def initialize_schema(conn):
        cur = conn.cursor()
        cur.execute(METADATA_SCHEMA_STMT)
        cur.execute(PAGES_SCHEMA_STMT)
        cur.execute('INSERT INTO tubs_metadata VALUES (?, ?)', (TUBS_VERSION, 'datetime now'))
        conn.commit()

    @staticmethod
    def find_toc_file(container):
        if not container:
            return None
        expected_path = None
        # If the container is a directory, look for toc.db inside
        if os.path.isdir(container):
            expected_path = os.path.join(container, TOC_FILENAME)
        else:
            # TODO: Add ability to look inside zipfile
            basename, _ = os.path.split(container)
            # workbook.tiff -> workbook.toc.db
            expected_path = f"{basename}.{TOC_FILENAME}"

        if expected_path and os.path.exists(expected_path):
            return expected_path
        return None

    def add_page(self, page, **kwargs):
        # kwargs could be:
        # - Page type
        pass

    def save_toc(self, file="toc.db"):
        # TODO: File needs to be in working directory if it's not explicit
        dest = sqlite3.connect(file)
        # This is going to require Python 3.7 or higher
        self.table_of_contents.backup(dest)

    # Return a dict of what's in the workbook
    # 
    def get_table_of_contents(self):
        return {
            "SomeGlobalProperty": "Foo",
            "Pages": [
                {"Page": 1, "FormType": "PS2_REV_DEC_2016", "File": "Some/Path/To/A/File.png"},
            ]
        }
