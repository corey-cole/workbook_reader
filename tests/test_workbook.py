#pylint: disable = line-too-long,no-self-use
"""
Exercise the workbook class.
"""
import os
import pytest
import tempfile
from unittest.mock import patch
from workbook_reader.workbook import Workbook


class TestWorkbook:
    """Collection of workbook tests"""

    def test_no_toc_for_missing_container(self):
        """Confirm raise on missing TOC file"""
        with pytest.raises(Exception, match=r"No table of contents found for container"):
            wb = Workbook(load_contents=True)
    
    def test_find_toc_file_for_none_container(self):
        results = Workbook.find_toc_file(None)
        assert results is None
    
    @patch('os.path.exists')
    def test_find_toc_file_for_directory(self, path_exists):
        path_exists.return_value = True
        results = Workbook.find_toc_file('/tmp')
        assert results == '/tmp/toc.db'
    
    @patch('os.path.exists')
    def test_find_toc_file_for_tiff(self, path_exists):
        """Confirm toc file is expected to be side-by-side with a single file container"""
        path_exists.return_value = True
        results = Workbook.find_toc_file('workbook.tiff')
        assert results == 'workbook.toc.db'
    
    @patch('os.path.exists')
    def test_find_toc_file_when_directory_is_missing_toc(self, path_exists):
        path_exists.return_value = False
        results = Workbook.find_toc_file('/tmp')
        assert results is None

    @patch('os.path.exists')
    def test_find_toc_file_when_tiff_file_has_no_toc(self, path_exists):
        path_exists.return_value = False
        results = Workbook.find_toc_file('workbook.tiff')
        assert results is None

    def test_save_toc(self):
        """This test is still a work in progress"""
        wb = Workbook(container="./")
        wb.add_page(filename='foo.tiff:1')
        results = wb.save_toc()
        assert 'toc.db' in results
        # TODO: Check contents
        os.remove(results)