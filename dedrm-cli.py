import logging
import os.path
from pathlib import Path

from DeDRM_plugin import adobekey, ignoblekey, kindlekey
from DeDRM_plugin.scriptinterface import (
    decryptepub,
    decryptk4mobi,
    decryptpdb,
    decryptpdf,
)
from DeDRM_plugin.simpleprefs import SimplePrefs

ext_map = [
    ([".epub"], decryptepub),
    ([".pdb"], decryptpdb),
    (
        [
            ".azw",
            ".azw1",
            ".azw3",
            ".azw4",
            ".prc",
            ".mobi",
            ".pobi",
            ".tpz",
            ".azw8",
            ".kfx",
            ".kfx-zip",
        ],
        decryptk4mobi,
    ),
    ([".pdf"], decryptpdf),
]


def get_prefs():
    description = [
        ["pids", "pidlist.txt"],
        ["serials", "seriallist.txt"],
        ["sdrms", "sdrmlist.txt"],
        ["outdir", "outdir.txt"],
    ]

    prefs = SimplePrefs("DeDRM", description).getPreferences()
    prefdir = prefs["dir"]

    adeptkeyfile = os.path.join(prefdir, "adeptkey.der")
    if not os.path.exists(adeptkeyfile):

        try:
            adobekey.getkey(adeptkeyfile)
        except Exception as e:
            logging.warning("Could not find %s: %s", adeptkeyfile, e)

    kindlekeyfile = os.path.join(prefdir, "kindlekey.k4i")
    if not os.path.exists(kindlekeyfile):

        try:
            kindlekey.getkey(kindlekeyfile)
        except Exception as e:
            logging.warning("Could not find %s: %s", kindlekeyfile, e)

    bnepubkeyfile = os.path.join(prefdir, "bnepubkey.b64")
    if not os.path.exists(bnepubkeyfile):
        try:
            ignoblekey.getkey(bnepubkeyfile)
        except Exception as e:
            logging.warning("Could not find %s: %s", bnepubkeyfile, e)

    return prefs


def decrypt_ebook(infile: Path, outdir: Path, rscpath: int) -> int:

    ext = infile.suffix.lower()

    for exts, func in ext_map:
        if ext in exts:
            return func(str(infile), str(outdir), rscpath)

    raise ValueError("Invalid file extension: {}".format(ext))


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path, help="eBook files to dedrm")
    parser.add_argument("--outdir", default=".", type=Path, help="Output directory")
    args = parser.parse_args()

    if not args.outdir.is_dir():
        parser.error("--outdir must point to an existing directory")

    prefs = get_prefs()
    rscpath = prefs["dir"]

    for infile in args.files:
        decrypt_ebook(infile, args.outdir, rscpath)
