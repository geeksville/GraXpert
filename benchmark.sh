set -e

USEGPU=true

echo "Running background extraction..."
time graxpert -cmd background-extraction -output /tmp/testout_bk -gpu $USEGPU tests/test_images/real_crummy.fits
echo "Running deconvolution (object)..."
time graxpert -cmd deconv-obj -output /tmp/testout_deconv -gpu $USEGPU /tmp/testout_bk.fits
echo "Running denoising..."
time graxpert -cmd denoising -output /tmp/testout_denoise -gpu $USEGPU /tmp/testout_deconv.fits