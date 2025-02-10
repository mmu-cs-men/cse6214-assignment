from image_cdn import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions


def upload_file_to_imagekit(file, filename):
    """
    Upload a file to ImageKit CDN.

    Args:
        file: The file object from request.FILES
        filename: Name to use for the uploaded file

    Returns:
        str: The URL of the uploaded file
        str: The file ID from ImageKit
    """
    try:
        options = UploadFileRequestOptions(
            use_unique_file_name=True,
            folder="/book_images/",
            is_private_file=False,
        )

        # Upload the file using its binary content
        result = imagekit.upload_file(
            file=file.read(), file_name=filename, options=options
        )

        return result.url, result.file_id
    except Exception as e:
        raise Exception(f"Failed to upload file to ImageKit: {str(e)}")


def delete_file_from_imagekit(file_id):
    """
    Delete a file from ImageKit CDN.

    Args:
        file_id: The ImageKit file ID to delete

    Returns:
        bool: True if deletion was successful
    """
    try:
        imagekit.delete_file(file_id=file_id)
        return True
    except Exception as e:
        raise Exception(f"Failed to delete file from ImageKit: {str(e)}")
