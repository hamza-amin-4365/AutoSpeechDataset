# full pipeline goes here

import sys
from scripts import download_audio


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    download_audio(sys.argv[1])