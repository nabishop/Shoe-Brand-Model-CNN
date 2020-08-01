from os import listdir

known_brands = ["24 kilates", "lacoste", "adidas", "new balance", "converse", "nike", "vans", "asics",
                "reebok", "puma", "dc", "prada", "gucci", "atmos", "black friday", "footshop",
                "under armour", "kangaroos", "jordan", "fila", "brooks", "clarks", "cts", "d lillard",
                "diadora", "etonic", "saucony", "ewing", "puma", "android", "apl", "bait", "brandblack",
                "british knights", "filling pieces", "le coq", "rise", "buscemi", "diamond supply co",
                "k-swiss", "k1x", "karhu", "la gear", "li-ning", "marxman", "mizuno", "onitsuka", "pf flyers", "pony",
                "red wing", "sebago", "sperry", "supra", "timberland", "super society"]


def label_brand(query):
    q = query.lower()

    for i in range(len(known_brands)):
        if q.find(known_brands[i]) != -1:
            return i

    if q.find("rebok") != -1 or q.find("question") != -1:
        return known_brands.index("reebok")

    if q.find("gel-lyte") != -1:
        return known_brands.index("asics")

    if q.find("kobe") != -1 or q.find("kyrie") != -1 or q.find("lebron") != -1 \
            or q.find("zoom kd") != -1 or q.find("curry") != -1 \
            or q.find("air force 1") != -1 or q.find("icarus") != -1 \
            or q.find("air max") != -1 or q.find("and1") != -1 or q.find("hyperlive") != -1 \
            or q.find("off-white") != -1 or q.find("sb dunk") != -1:
        return known_brands.index("nike")

    if q.find("yeezy") != -1 or q.find("human made") != -1 or q.find("superstar") != -1 or q.find("t-mac") != -1 \
            or q.find("zx flux") != -1 or q.find("tubular") != -1 or q.find("tubluar") != -1:
        return known_brands.index("adidas")

    if q.find("trail buster") != -1:
        return known_brands.index("new balance")

    return -1
