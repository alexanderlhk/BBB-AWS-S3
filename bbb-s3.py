import os, glob, shutil, boto3, magic
from botocore.exceptions import NoCredentialsError
mime = magic.Magic(mime=True)
## Configuration Part 
BUCKET_NAME = ''
DELETE_SERVER_FILES = True ## Set False (F should be capital) if you don't want to delete files from bbb-server

def upload_to_aws(local_file, bucket, s3_file):
    ctype = mime.from_file(local_file) 
    s3 = boto3.client('s3')

    try:
        s3.upload_file(local_file, bucket, s3_file, ExtraArgs={'ContentType': ctype, 'ACL': "public-read"}) 
        return True
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("\nFile not found\n")
    except NoCredentialsError: 
        return False

def getListOfFiles(dirName): 
    listOfFile = os.listdir(dirName)
    allFiles = list() 
    for entry in listOfFile: 
        fullPath = os.path.join(dirName, entry) 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles     

def getListOfDirs(path):
    return [os.path.basename(x) for x in filter(
        os.path.isdir, glob.glob(os.path.join(path, '*')))]

def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))

def main():
    
    dirName = os.getcwd(); 
    listOfFiles = getListOfFiles(dirName) 
    listOfDirs = getListOfDirs(dirName)
    for elem in listOfFiles:
        listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    last_relative_path = "test"
    for elem in listOfFiles:  
        relative_path = elem.replace(dirName,'')[1:]
        if(relative_path!='bbb-s3.py'):
            print("Last path was "+last_relative_path+"\n")
            print("Current path is "+relative_path.split('/')[-1]+"\n")
            if(last_relative_path=='metadata.xml' and relative_path.split('/')[-1]=='metadata.xml'):
                print("This is already uploaded")
            else:
                print("\nUploading "+relative_path)    
                uploaded = upload_to_aws(elem, BUCKET_NAME, relative_path)
                if(uploaded and DELETE_SERVER_FILES):
                    if "metadata.xml" not in elem:
                        remove(elem)
                else:
                    print("\nNot able to delete files from your bbb-server, check file if its uploaded")
        last_relative_path = relative_path.split('/')[-1]
        
        
        
if __name__ == '__main__':
    main()
