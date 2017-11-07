import os
import sys

import cv2
import numpy as np
from matplotlib.pyplot import imsave
from scipy import misc

from preprocess_images import generate_adaptive_bw_image
from unet_online_hint import get_unet


def main():
    im_height = 256
    im_width = 256
    main_model, model_name = get_unet(im_width, im_height)

    weights_file = "weights/UNET-ONLINE-HINTED.hdf5"

    main_model.load_weights(weights_file)
    is_directory = True

    try:
        files = os.listdir(sys.argv[2])
    except NotADirectoryError as e:
        is_directory = False
        files = [sys.argv[2]]

    for file in files:
        try:
            color_img = misc.imresize(
                misc.imread(os.path.join(sys.argv[2], file)),
                (256, 256)
            )[:, :, :3]
        except NotADirectoryError:
            color_img = misc.imresize(
                misc.imread(file),
                (256, 256)
            )[:, :, :3]

        imsave("results/color.png", color_img)
        if len(sys.argv) > 3 and not is_directory:
            bw_img = misc.imread(sys.argv[3])
            # bw_img = np.stack((bw_img, bw_img, bw_img), axis=2)
            # imshow(bw_img)
            # show()
            load_and_resize = misc.imresize(bw_img, (256, 256))[:, :, :3]

            bw_img = generate_adaptive_bw_image(load_and_resize)[..., None]
        else:
            bw_img = generate_adaptive_bw_image(color_img)[..., None]

        imsave("results/lines.png", bw_img[:, :, 0], cmap='gray')

        hint1 = color_img
        # hint1 = cv2.GaussianBlur(color_img, (0, 0), 10)
        hint1 = hint1 * 0.3 + np.ones_like(hint1) * 0.7 * 255
        # imshow(np.uint8(hint1))
        # show()
        #
        # spliced = np.concatenate((bw_img, hint1), axis=2) / 255
        #
        # prediction = main_model.predict(spliced[None, ...])[0] * 255
        #
        # imshow(np.uint8(prediction))
        # show()

        hint2 = cv2.GaussianBlur(color_img, (0, 0), 30)

        # imshow(np.uint8(hint2))
        # show()
        #
        # spliced = np.concatenate((bw_img, hint2), axis=2) / 255
        #
        # prediction = main_model.predict(spliced[None, ...])[0] * 255
        #
        # imshow(np.uint8(prediction))
        # show()
        for color_blur_slider in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7]:
            hint3 = color_blur_slider * hint1 + (1 - color_blur_slider) * hint2
            imsave("results/hint " + str(color_blur_slider) + ".png",
                   np.uint8(hint3))

            spliced = np.concatenate((bw_img, hint3), axis=2) / 255

            prediction = main_model.predict(spliced[None, ...])[0] * 255

            imsave("results/prediction " + str(color_blur_slider) + ".png",
                   np.uint8(prediction))


if __name__ == "__main__":
    main()
