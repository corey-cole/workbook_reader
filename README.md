# Workbook Reader

## Background
This is an exploratory project to apply image processing techniques in order to extract data from
fisheries observer workbooks.  While this project runs on a desktop/laptop computer connected to the internet, the intent
is to create something that can be used in an environment where compute and/or bandwidth are highly constrained.

## Getting Started
In order to use this, you'll need to find/create an original workbook page as well as an example image to
register against it.  SPC maintains a library of current master forms within the [OFP area](https://oceanfish.spc.int/en/data-collection/241-data-collection-forms) of their website.  Example "scans" are easier to create using a digital camera or a consumer grade scanner.

An example of using the utility is shown below:
```bash
python workbook_reader/align_images.py --scan fake_scan_1.jpg --original ps2_data_page.png --debug
```

## Form Conversion Notes
Example scans were created by splitting the PDF via MacOS preview.
PNG versions of the forms were created with ImageMagick convert:

```
# density 300 create a huge image that isn't much clearer than 150
convert -quality 100 -density 150 ps2_data_page.pdf ps2_data_page.png
```

## Useful Resources
This research is based on examples from the [Pyimagesearch Blog](https://www.pyimagesearch.com/blog/).