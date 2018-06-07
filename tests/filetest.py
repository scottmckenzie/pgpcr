def cmpfiles(test, a, b):
    with open(a, "rb") as f1, open(b, "rb") as f2:
        test.assertEqual(f1.read(), f2.read())

