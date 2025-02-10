import base64
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from imagekitio import ImageKit

imagekit = ImageKit(
    private_key="private_+kRnJCZfoiTkm6WmQmwXlxrx4ew=",
    public_key="public_k1uw6aQxX2FvkMWGqe/yFK4g1fU=",
    url_endpoint="https://ik.imagekit.io/softwareengbookstore",
)


def upload_file_to_imagekit(file, filename):
    """
    Upload a file to ImageKit CDN.

    :param file: The file object from request.FILES
    :type file: django.core.files.uploadedfile.UploadedFile
    :param filename: Name to use for the uploaded file
    :type filename: str
    :returns: A tuple containing the URL of the uploaded file and the file ID from ImageKit
    :rtype: tuple[str, str]
    :raises Exception: If file upload fails
    """
    try:
        # Read the file and convert to base64
        file_content = file.read()
        base64_file = base64.b64encode(file_content).decode('utf-8')
        
        options = UploadFileRequestOptions(
            use_unique_file_name=True,
            folder="/book_images/",
        )

        # Upload the file using base64 content
        result = imagekit.upload_file(
            file=base64_file,
            file_name=filename,
            options=options,
        )

        return result.url, result.file_id
    except Exception as e:
        raise Exception(f"Failed to upload file: {str(e)}")


def delete_file_from_imagekit(file_id):
    """
    Delete a file from ImageKit CDN.

    :param file_id: The ImageKit file ID to delete
    :type file_id: str
    :returns: True if deletion was successful
    :rtype: bool
    :raises Exception: If file deletion fails
    """
    try:
        imagekit.delete_file(file_id=file_id)
        return True
    except Exception as e:
        raise Exception(f"Failed to delete file: {str(e)}")
