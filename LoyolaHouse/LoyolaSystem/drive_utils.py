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
                                    'GoogleDrive_JSON', 'loyolaproject-b43371fe4c1e.json')
        
        # Verify the credentials file exists
        if not os.path.exists(credentials_path):
            logging.error(f"Credentials file not found at: {credentials_path}")
            return None
            
        # Check if the credentials file is readable and valid JSON
        try:
            import json
            with open(credentials_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Credentials file is not valid JSON: {credentials_path}")
            return None
        except Exception as e:
            logging.error(f"Error reading credentials file: {e}")
            return None
        
        # Define the scopes needed for Google Drive
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Create credentials using the service account file
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES)
        except Exception as e:
            if 'invalid_grant' in str(e) and 'JWT Signature' in str(e):
                logging.error("Invalid JWT Signature error: The service account credentials may be expired or invalid.")
                logging.error("Please generate new service account credentials from the Google Cloud Console.")
            else:
                logging.error(f"Error creating credentials: {e}")
            return None
        
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
    media = None
    try:
        drive_service = get_drive_service()
        if not drive_service:
            logging.error("Failed to create Drive service")
            return None, None
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
            
            temp_file_path = temp_file.name
            # Make sure the file is fully written and closed before proceeding
            temp_file.flush()
            os.fsync(temp_file.fileno())
        
        logging.info(f"Temporary file created at: {temp_file_path}")
        
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
        try:
            media = MediaFileUpload(
                temp_file_path,
                mimetype=mime_type,
                resumable=True
            )
        except Exception as e:
            logging.error(f"Error creating MediaFileUpload: {e}")
            return None, None
        
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
        # Clean up resources
        if media:
            try:
                # Close any open file handles in the MediaFileUpload object
                if hasattr(media, '_fd') and media._fd:
                    media._fd.close()
            except Exception as e:
                logging.error(f"Error closing media file handle: {e}")
                
        # Clean up the temporary file with retry logic
        if temp_file_path and os.path.exists(temp_file_path):
            for attempt in range(3):  # Try up to 3 times
                try:
                    # Small delay to ensure file handles are released
                    import time
                    time.sleep(0.5)
                    os.unlink(temp_file_path)
                    logging.info(f"Temporary file {temp_file_path} removed on attempt {attempt+1}")
                    break  # Success, exit the loop
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        logging.error(f"Failed to remove temporary file after 3 attempts: {e}")
                    else:
                        logging.warning(f"Attempt {attempt+1} to remove file failed: {e}, retrying...")
