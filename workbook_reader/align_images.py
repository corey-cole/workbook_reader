"""Form image alignment utility"""
# pylint: disable=invalid-name
import sys

import numpy as np
import imutils
import cv2
import click


def image_as_grayscale(image):
    """Convert to grayscale if required"""
    if image is None:
        return None
    if len(image.shape) > 2:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image
    

def align_images(image, template, maxFeatures=500, keepPercent=0.2, debug=False):
    imageGray = image_as_grayscale(image)
    templateGray = image_as_grayscale(template)

    # Use ORB to detect keypoints and extract features
    orb = cv2.ORB_create(maxFeatures)
    (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
    (kpsB, descsB) = orb.detectAndCompute(templateGray, None)

    # match features
    method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
    matcher = cv2.DescriptorMatcher_create(method)
    matches = matcher.match(descsA, descsB, None)

    # Sort by distance (similarity)
    matches = sorted(matches, key=lambda x:x.distance)

    keep = int(len(matches) * keepPercent)
    matches = matches[:keep]

    # Visualize for debug purposes
    if debug:
        matchedVis = cv2.drawMatches(image, kpsA, template, kpsB, matches, None)
        matchedVis = imutils.resize(matchedVis, width=1000)
        cv2.imshow("Matched Keypoints", matchedVis)
        cv2.waitKey(0)
    
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")

    for (i, m) in enumerate(matches):
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt
    
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)

    (h, w) = template.shape[:2]
    aligned = cv2.warpPerspective(image, H, (w, h))

    return aligned

@click.command()
@click.option('--scan', type=click.Path(exists=True), help='Scanned image')
@click.option('--original', type=click.Path(exists=True), help='Original template to match against')
@click.option('--max-features', default=1500, help='Number of features to match')
@click.option('--debug', is_flag=True)
def main(scan, original, max_features, debug):
    # In the original example, this is done in another file.  However, we're going to
    # do this inline for quick testing.
    image = cv2.imread(scan)
    if image is None:
        print(f"Unable to read image {scan}")
        sys.exit(1)
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # TODO: Thresholding is a WIP.  Might need to keep the color image for more context
    #threshold_value, image_bin = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #print(f"Otsu threshold: {threshold_value}")
    #cv2.imshow("Threshold Scan", image_bin)
    #cv2.waitKey(0)
    # TODO: Also possible that the issue is that template and scan need to be thresholded
    # Can't have one grayscale and one B&W?
    template = cv2.imread(original)
    if template is None:
        print(f"Unable to read template file {template}")
        sys.exit(1)

    print("Aligning images...")
    # The default value of 500 produces terrible results with my example scans.
    # There's another project in here to iterate through some feature counts/keep percentages
    # compared to CPU/memory/time and determine what's an appropriate value.
    aligned = align_images(image, template, maxFeatures=max_features, debug=debug)

    cv2.imwrite('registered_scan.png', aligned)

    if debug:
        aligned = imutils.resize(aligned, width=700)
        template = imutils.resize(template, width=700)

        stacked = np.hstack([aligned, template])

        overlay = template.copy()
        output = aligned.copy()
        cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)

        # Show the two alignment visualizations
        cv2.imshow("Image Alignment Stacked", stacked)
        cv2.imshow("Image Alignment Overlay", output)
        cv2.waitKey(0)

        # When we have a better scan, see if this mostly shows the handwritten input
        #img_diff = cv2.bitwise_not(cv2.subtract(output, template))
        #cv2.imshow("Image Delta", img_diff)
        #cv2.waitKey(0)


if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
