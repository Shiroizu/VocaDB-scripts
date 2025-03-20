import time


def create_songlists(session, title, song_ids: list[str], max_length=200):
    counter = 1

    for i in range(1 + len(song_ids) // max_length):
        sublist = song_ids[i * max_length : (i + 1) * max_length]
        if not sublist:
            break

        if len(song_ids) > max_length:
            title += f" ({counter})"
            print(f"Posting sublist {counter}")

        else:
            print("Posting songlist")

        songlist = {"songLinks": [], "author": {"id": 329}, "name": title}

        order = 1
        for song_id in sublist:
            sonlist_item = {"order": order, "song": {"id": int(song_id)}}
            songlist["songLinks"].append(sonlist_item)
            order += 1

        songlist_request = session.post(
            "https://vocadb.net/api/songLists", json=songlist
        )
        songlist_request.raise_for_status()
        counter += 1
        time.sleep(3)
