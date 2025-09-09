set -e

echo "Running background extraction..."
time ~/.local/bin/graxpert -cmd background-extraction -output /tmp/testout_bk -gpu false tests/test_images/real_crummy.fits
echo "Running deconvolution (object)..."
time ~/.local/bin/graxpert -cmd deconv-obj -output /tmp/testout_deconv -gpu false /tmp/testout_bk.fits
echo "Running denoising..."
time ~/.local/bin/graxpert -cmd denoising -output /tmp/testout_denoise -gpu false /tmp/testout_deconv.fits