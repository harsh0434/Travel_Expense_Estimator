import os
import shutil
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_backup():
    try:
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'backups/backup_{timestamp}'
        os.makedirs(backup_dir, exist_ok=True)

        # Backup user database
        if os.path.exists('users_db.json'):
            shutil.copy2('users_db.json', os.path.join(backup_dir, 'users_db.json'))
            logger.info('User database backed up successfully')

        # Backup application logs
        if os.path.exists('app.log'):
            shutil.copy2('app.log', os.path.join(backup_dir, 'app.log'))
            logger.info('Application logs backed up successfully')

        # Backup environment variables
        env_vars = {
            'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
            'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
            'TWILIO_ACCOUNT_SID': os.getenv('TWILIO_ACCOUNT_SID'),
            'TWILIO_AUTH_TOKEN': os.getenv('TWILIO_AUTH_TOKEN'),
            'TWILIO_PHONE_NUMBER': os.getenv('TWILIO_PHONE_NUMBER')
        }
        with open(os.path.join(backup_dir, 'env_vars.json'), 'w') as f:
            json.dump(env_vars, f, indent=4)
        logger.info('Environment variables backed up successfully')

        # Create backup manifest
        manifest = {
            'timestamp': timestamp,
            'backup_dir': backup_dir,
            'files_backed_up': os.listdir(backup_dir)
        }
        with open(os.path.join(backup_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=4)
        logger.info('Backup manifest created successfully')

        return True, backup_dir

    except Exception as e:
        logger.error(f'Backup failed: {str(e)}')
        return False, str(e)

def restore_backup(backup_dir):
    try:
        # Verify backup directory exists
        if not os.path.exists(backup_dir):
            raise Exception('Backup directory not found')

        # Restore user database
        if os.path.exists(os.path.join(backup_dir, 'users_db.json')):
            shutil.copy2(os.path.join(backup_dir, 'users_db.json'), 'users_db.json')
            logger.info('User database restored successfully')

        # Restore environment variables
        if os.path.exists(os.path.join(backup_dir, 'env_vars.json')):
            with open(os.path.join(backup_dir, 'env_vars.json'), 'r') as f:
                env_vars = json.load(f)
            for key, value in env_vars.items():
                if value:
                    os.environ[key] = value
            logger.info('Environment variables restored successfully')

        return True, 'Backup restored successfully'

    except Exception as e:
        logger.error(f'Restore failed: {str(e)}')
        return False, str(e)

if __name__ == '__main__':
    # Create backup
    success, result = create_backup()
    if success:
        print(f'Backup created successfully in {result}')
    else:
        print(f'Backup failed: {result}') 