# fingo technical design

Images can be put in a directory tree, but will be put in albums based on their metadata files, which are generated by fingo and which can be edited to add albums, tags and other information, like descriptions.

The metadata is put in [YAML](https://en.wikipedia.org/wiki/YAML) files, which are named after the [image hash](https://github.com/JohannesBuchner/imagehash) of the pictures, specifically the [dHash variant](http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html).

For example, the following bunch of images:

```
nature/IMG_1001.jpg
nature/IMG_1080.jpg
nature/dunes/IMG_1081.jpg
nature/sun/IMG_3089.jpg
photolog/IMG_1001.jpg
tech/IMG_4242.jpg
tech/screenshots/firefox.png
```
