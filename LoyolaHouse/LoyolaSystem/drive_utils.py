import os
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_drive_service():
    """
    Authenticates with Google Drive API using service account credentials
    and returns a Google Drive service object.
    """
    try:
        # Path to the service account credentials file
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'Assests', 'loyolaproject-8e285f4f17a0.json')
        
        # Verify the credentials file exists
        if not os.path.exists(credentials_path):
            logging.error(f"Credentials file not found at: {credentials_path}")
            return None
        
        # Define the scopes needed for Google Drive
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Create credentials using the service account file
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES)
        
        # Build the Drive service
        service = build('drive', 'v3', credentials=credentials)
        
        return service
    except Exception as e:
        logging.error(f"Error creating Drive service: {e}")
        return None

def upload_file_to_drive(file_obj, file_name):
    """
    Uploads a file to Google Drive using the service account.
    
    Args:
        file_obj: The file object to upload
        file_name: Name to give the file in Google Drive
        
    Returns:
        tuple: (file_id, file_url) if successful, (None, None) otherwise
    """
    temp_file_path = None
    try:
        # Get the Drive service
        drive_service = get_drive_service()
        if not drive_service:
            logging.error("Failed to create Drive service")
            return None, None
        
        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write the content of the uploaded file to the temporary file
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        logging.info(f"Temporary file created at: {temp_file_path}")
        
        # Determine the MIME type based on the file extension
        mime_type = 'application/octet-stream'  # Default MIME type
        if '.' in file_name:
            ext = file_name.split('.')[-1].lower()
            if ext in ['pdf']:
                mime_type = 'application/pdf'
            elif ext in ['doc', 'docx']:
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif ext in ['xls', 'xlsx']:
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif ext in ['ppt', 'pptx']:
                mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            elif ext in ['jpg', 'jpeg']:
                mime_type = 'image/jpeg'
            elif ext in ['png']:
                mime_type = 'image/png'
        
        logging.info(f"Using MIME type: {mime_type} for file: {file_name}")
        
        # Define file metadata - only include writable fields
        file_metadata = {
            'name': file_name
        }
        
        # Create a MediaFileUpload object
        media = MediaFileUpload(
            temp_file_path,
            mimetype=mime_type,
            resumable=True
        )
        
        # Upload the file to Google Drive
        logging.info("Uploading file to Google Drive...")
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        file_id = file.get('id')
        if not file_id:
            logging.error("File upload succeeded but no file ID was returned")
            return None, None
            
        logging.info(f"File uploaded successfully with ID: {file_id}")
        
        # Make the file publicly accessible with a link
        logging.info("Setting file permissions...")
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        
        drive_service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        logging.info("File permissions set successfully")
        
        # Get the webViewLink
        web_view_link = file.get('webViewLink')
        if not web_view_link:
            # If webViewLink wasn't returned in the create call, get it now
            file = drive_service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            web_view_link = file.get('webViewLink')
        
        logging.info(f"File web view link: {web_view_link}")
        
        # Return the file ID and web view link
        return file_id, web_view_link
    
    except Exception as e:
        logging.error(f"Error uploading file to Google Drive: {e}")
        return None, None
    
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logging.info(f"Temporary file {temp_file_path} removed")
            except Exception as e:
                logging.error(f"Error removing temporary file: {e}")
