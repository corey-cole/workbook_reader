"""Class representing a filled out workbook scan"""
import os
import sqlite3

# Version information and any other global properties that apply.
# While I would generally expect a workbook to contain pages that are all the same edition
# I can also easily imagine a scenario where it does not:
# > Running out of pages and falling back to another older set
# > Observer being accidentally provided with mixed pages.
# As such, each page needs to record it's own type & edition.
METADATA_SCHEMA_STMT = """
CREATE TABLE tubs_metadata (tubs_version integer, last_saved text)
""".strip()

# Filename needs to include internal location for archives/TIFF files
# Probably want to use something like 'workbook.tiff:1'
PAGES_SCHEMA_STMT = """
CREATE TABLE wb_pages (
    page_id INTEGER PRIMARY KEY ASC,
    filename text,
    page_number integer,
    form_type text,
    registered_filename text,
    file_checksum text,
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
        self.contents_file = TOC_FILENAME
        if not load_contents:
            self.table_of_contents = sqlite3.connect(':memory:')
            Workbook.initialize_schema(self.table_of_contents)
        else:
            # Load an existing file, failing if we cannot
            toc_file = Workbook.find_toc_file(container)
            if not toc_file:
                raise Exception(f"No table of contents found for container '{container}'")
            self.contents_file = toc_file
            # TODO: Validate schema
            self.table_of_contents = sqlite3.connect(self.contents_file)
        self.container = container
        self.properties = properties or {}

    def add_registered_page(self, page_id, filename):
        # TODO: This is pretty raw and assumes that we know the page_id value
        # Long term this should be a little friendlier to use.
        with self.table_of_contents:
            self.table_of_contents.execute(
                'UPDATE wb_pages SET registered_filename = ? WHERE page_id = ?', 
                (filename, page_id)
            )
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
        with conn:
            conn.execute(METADATA_SCHEMA_STMT)
            conn.execute(PAGES_SCHEMA_STMT)
            conn.execute('INSERT INTO tubs_metadata VALUES (?, ?)', (TUBS_VERSION, 'datetime now'))

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
            basename, _ = os.path.splitext(container)
            # workbook.tiff -> workbook.toc.db
            expected_path = f"{basename}.{TOC_FILENAME}"

        if expected_path and os.path.exists(expected_path):
            return expected_path
        return None

    def add_page(self, **kwargs):
        if 'filename' not in kwargs:
            # What do we want to do here?
            return
        values = {
            'filename': kwargs['filename'],
            'page_number': kwargs.get('page_number', -1),
            'form_type': kwargs.get('form_type','UNKNOWN'),
            'registered_filename': kwargs.get('registered_filename', None),
            'file_checksum': kwargs.get('file_checksum', None),
            'comments': kwargs.get('comments', None),
            'excluded': kwargs.get('excluded', False)
        }
        # https://stackoverflow.com/a/16698310
        with self.table_of_contents:
            self.table_of_contents.execute("""
                INSERT INTO wb_pages (filename, page_number, form_type, registered_filename, file_checksum, comments, excluded)
                VALUES (:filename, :page_number, :form_type, :registered_filename, :file_checksum, :comments, :excluded);
                """.strip(),
                values
            )

    def save_toc(self, file=None):
        target_file = file or self.contents_file
        # TODO: File needs to be in working directory if it's not explicit
        dest = sqlite3.connect(target_file)
        # This is going to require Python 3.7 or higher
        self.table_of_contents.backup(dest)
        return target_file

    # Return a dict of what's in the workbook
    # 
    def get_table_of_contents(self):
        return {
            "SomeGlobalProperty": "Foo",
            "Pages": [
                {"Page": 1, "FormType": "PS2_REV_DEC_2016", "File": "Some/Path/To/A/File.png"},
            ]
        }
