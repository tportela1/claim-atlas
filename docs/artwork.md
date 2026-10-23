# Artwork and export quality

The logo SVGs in skills/claim-atlas/assets are the editable vector masters. The README uses SVG so text and shapes remain crisp at any display density. Transparent PNG logo exports are supplied at 1024px for the mark and 2040px for the wordmarks.

The large docs/logo-preview.svg and preview-desktop.svg are vector presentation artwork. The report overview is explicitly illustrative, with fictitious content; it is not a pixel-perfect screenshot of the HTML report. Genuine high-resolution PNG counterparts are rendered from these vectors, not enlarged from compressed screenshots.

Actual browser captures are kept separately under docs/screenshots with truthful .jpg extensions. The phone PNG preserves its native capture size; converting it to PNG does not restore detail lost in the original JPEG.

To regenerate raster exports, use Node.js and the optional sharp package: `node tools/export-previews.mjs`. The tool accepts SHARP_MODULE_PATH for an externally managed sharp installation. This dependency is only for artwork export; skill installation, research helpers, report rendering and normal checks remain Python standard-library only. Edit the vector master, then export; do not upscale a screenshot and label it high resolution.

Tests validate PNG signatures, minimum presentation dimensions, and byte-for-byte preservation of binary assets in release packages.
