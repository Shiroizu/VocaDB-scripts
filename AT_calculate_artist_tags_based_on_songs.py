import argparse

from tabulate import tabulate
from vdbpy.api.artists import get_artist_by_id
from vdbpy.api.songs import get_songs_by_artist_id
from vdbpy.utils.logger import get_logger

""" Example output:

Artist 'Clean Tears' (Ar/20) - Most common tags:
|   entry_count |   votes | name                            | category     |   tag_id | tag_added   |
|---------------|---------|---------------------------------|--------------|----------|-------------|
|           119 |     302 | trance                          | Genres       |      435 | True        |
|            41 |      63 | self-remix                      | Sources      |      392 | False       |
|            29 |      72 | EDM                             | Genres       |     1552 | True        |
|            24 |      40 | drum and bass                   | Genres       |      108 | True        |
|            22 |      50 | electropop                      | Genres       |      124 | True        |
|            21 |      48 | house                           | Genres       |      196 | True        |
|            17 |      31 | good tuning                     | Subjective   |     4582 | True        |
|            17 |      31 | glitchy voice                   | Vocalists    |     7853 | True        |
|            16 |      23 | self-cover                      | Sources      |      391 | False       |
|            14 |      32 | progressive house               | Genres       |      350 | True        |
|            14 |      22 | RnB                             | Genres       |      375 | True        |
|            14 |      21 | pop                             | Genres       |      341 | True        |
|            13 |      28 | dubstep                         | Genres       |      112 | True        |
|            12 |      21 | free                            | Distribution |      160 | False       |
|            12 |      19 | cover                           | Sources      |       74 | False       |
|            12 |      20 | English subtitles               | Sources      |     7406 | False       |
|            11 |      14 | instrumental                    | Vocalists    |      208 | False       |
|            11 |      22 | upgraded voicebank              | Sources      |     6333 | False       |
|            11 |      14 | cool                            | Subjective   |     6565 | False       |
|            11 |      27 | progressive trance              | Genres       |      352 | True        |
|            10 |      14 | extended version                | Sources      |     3068 | False       |
|            10 |      16 | long intro                      | Sources      |     4905 | False       |
|            10 |      17 | technopop                       | Genres       |     1698 | True        |

"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "artist_id",
        type=int,
        help="Artist id to check.",
    )
    parser.add_argument(
        "--only_with_pvs",
        help="Only include entries with PVs.",
        action="store_true",
    )
    parser.add_argument(
        "--include_collabs",
        help="Include entries where the artist is only participating.",
        action="store_true",
    )

    return parser.parse_args()


if __name__ == "__main__":
    logger = get_logger("calculate_artist_tags_based_on_songs")
    args = parse_args()

    params = {
        "fields": "Tags",
        "onlyWithPvs": args.only_with_pvs,
        "artistParticipationStatus": "OnlyMainAlbums",
    }

    if args.include_collabs:
        params["artistParticipationStatus"] = "Everything"

    artist_id = args.artist_id
    songs_by_artist = get_songs_by_artist_id(artist_id, params)
    logger.info(f"\nFound {len(songs_by_artist)} songs")
    tag_counts = {}
    for song in songs_by_artist:
        """ count	1
            tag
                additionalNames	"kpop"
                categoryName	"Genres"
                id	            1700
                name	        "K-pop"
                urlSlug	        "k-pop"
        """
        for tag in song["tags"]:
            tag_data = tag["tag"]
            tag_id = tag_data["id"]
            tag_votes = tag["count"]
            if tag_id not in tag_counts:
                tag_counts[tag_id] = {
                    "entry_count": 1,
                    "votes": tag_votes,
                    "name": tag_data["name"],
                    "category": tag_data["categoryName"],
                    "tag_id": tag_id,
                }
            else:
                tag_counts[tag_id]["entry_count"] += 1
                tag_counts[tag_id]["votes"] += tag_votes

    artist_entry = get_artist_by_id(artist_id, fields="Tags")
    artist_entry_tag_ids = [tag["tag"]["id"] for tag in artist_entry["tags"]]
    tags_to_print = tag_counts.values()
    sorted_by_entry_count = sorted(
        tags_to_print, key=lambda x: x["entry_count"], reverse=True
    )
    for tag in sorted_by_entry_count:
        if tag["tag_id"] in artist_entry_tag_ids:
            tag["tag_added"] = True
        else:
            tag["tag_added"] = False

    participation = "main songs" if not args.include_collabs else "including collabs"
    logger.info(
        f"\nArtist '{artist_entry['name']}' (Ar/{artist_id}) - Most common tags ({participation}):"
    )
    logger.info(tabulate(sorted_by_entry_count, headers="keys", tablefmt="github"))
