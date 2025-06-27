from PIL import Image, ImageDraw, ImageFilter

# Parameters
size = 1024  # Square image: 1024x1024
fade_width = size // 0.5  # Controls softness of fade

# Step 1: Create radial alpha mask
mask = Image.new("L", (size, size), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, size, size), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(radius=fade_width * 0.1))

# Step 2: Create black image with alpha
black_image = Image.new("RGBA", (size, size), (0, 0, 0, 255))

# Step 3: Invert mask for transparency in center
alpha = Image.eval(mask, lambda a: 255 - a)
black_image.putalpha(alpha)

# Save the result
black_image.save("vignette.png")
black_image.show()
