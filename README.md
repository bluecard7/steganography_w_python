# Steganography with Python
This Python script hides and recovers messages from certain PNG images in pure Python.
It assumes an RGB image and the message is in stdin.

It serves as a proof of concept for what I really wanted to do, which was a steganography implementation in C.
I had complications integrating zlib in my C implementation, so I decided to just work with Python to see how everything would work once I got it to integrate.

As of 10/4/19, this script can only recover up to 380 characters.
It also doesn't maintain the appearance of some png images.
I don't know why this is the case yet.

To encode:
- cd src
- cat message.txt | python steganography.py encode

To decode: 
- cd src
- python steganography.py decode

## Link to post about this project
- [https://bluecard7.github.io/posts/png_steganography.html](https://bluecard7.github.io/posts/png_steganography.html)