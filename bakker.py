⁸

mrl1 = "P<USAGORDON<<STEVE<<<<<<<<<<<<<<<<<<<<<<<<<"
mrl2 = "75726045510USA4245682M8312915724<2126<<<<<<<"

(h, w) = image.shape[:2]
center = (w // 2, h // 2)

# Compute the rotation matrix
M = cv2.getRotationMatrix2D(center, angle, 1.0)

# Compute the new bounding dimensions after rotation
cos = np.abs(M[0, 0])
sin = np.abs(M[0, 1])

new_w = int((h * sin) + (w * cos))
new_h = int((h * cos) + (w * sin))

# Adjust the rotation matrix to consider the translation
M[0, 2] += (new_w - w) / 2
M[1, 2] += (new_h - h) / 2

# Rotate the image with the new bounding dimensions
deskewed = cv2.warpAffine(image, M, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

return deskewed
