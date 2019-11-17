from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

import zipfile, sys, os, re

class UnzipFileOperator(BaseOperator):

    template_fields = ('zip_file', 'extract_to')
    ui_color = '#b05b27'

    @apply_defaults
    def __init__(
            self,
            zip_file,
            extract_to,
            *args, **kwargs):
        """
        :param zip_file: file to unzip (including path to file)
        :type zip_file: string
        :param extract_to: where to extract zip file to
        :type extract_to: string
        """

        super(UnzipFileOperator, self).__init__(*args, **kwargs)
        self.zip_file = zip_file
        self.extract_to = extract_to

    def execute(self, context):

        self.log.info("UnzipFileOperator execution started.")
        self.log.info("Unzipping '" + self.zip_file + "' to '" + self.extract_to + "'.")

        zf = zipfile.ZipFile(self.zip_file, 'r')

        for m in zf.infolist():
            
            data = zf.read(m) # extract zipped data into memory
            disk_file_name = m.filename.encode('ascii', 'ignore').decode('utf-8') # convert unicode file path to utf8
            dir_name = os.path.join(self.extract_to, os.path.dirname(disk_file_name)) # get directory of file
            re.sub('[^.-A-Za-z0-9_\/]+', '', disk_file_name) # remove special characters

            try:
                os.makedirs(dir_name) # make directory
            except OSError as e:
                if e.errno == os.errno.EEXIST:
                    pass
                else:
                    raise
            except Exception as e:
                raise

            self.log.info("writing data to" + os.path.join(self.extract_to, disk_file_name))

            with open(os.path.join(self.extract_to, disk_file_name), 'wb') as fd:
                fd.write(data) # write data to file

        zf.close()

        self.log.info("UnzipFileOperator done.")
