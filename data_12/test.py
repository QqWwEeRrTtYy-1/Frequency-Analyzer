from charset_normalizer import CharsetNormalizerMatches as cnm

text_str = str(cnm.from_path("test.txt").best().first())
print(text_str)