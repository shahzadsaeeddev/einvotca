
def get_media_info(media_url):
    from urllib.parse import urlparse
    import os, mimetypes

    parsed = urlparse(media_url)
    file_name = os.path.basename(parsed.path)

    if not file_name:
        file_name = "file"

    file_name = str(file_name)

    mime_type, _ = mimetypes.guess_type(file_name)

    if mime_type:
        if mime_type.startswith("image"):
            media_type = "image"
        elif mime_type.startswith("video"):
            media_type = "video"
        elif mime_type.startswith("audio"):
            media_type = "audio"
        else:
            media_type = "document"
    else:
        media_type = "document"

    return media_type, file_name

