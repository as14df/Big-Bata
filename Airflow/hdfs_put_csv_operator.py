from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException

from hooks.hdfs_hook import HdfsHook

import os, shutil

class HdfsPutCsvOperator(BaseOperator):

    template_fields = ('local_file', 'remote_file', 'hdfs_conn_id')
    ui_color = '#fcdb03'

    @apply_defaults
    def __init__(
            self,
            local_file,
            remote_file,
            hdfs_conn_id,
            *args, **kwargs):
        """
        :param local_file: file to upload to HDFS
        :type local_file: string
        :param remote_file: hdfs upload location
        :type remote_file: string
        :param hdfs_conn_id: airflow connection id to hdfs
        :type hdfs_conn_id: string
        """

        super(HdfsPutCsvOperator, self).__init__(*args, **kwargs)
        self.local_file = local_file
        self.remote_file = remote_file
        self.hdfs_conn_id = hdfs_conn_id

    def execute(self, context):

        self.log.info("HdfsPutCsvOperator execution started.")

        self.log.info("Upload file '" + self.local_file + "' to hdfs '" + self.remote_file + "'.'")

        hh = HdfsHook(hdfs_conn_id=self.hdfs_conn_id)

        i=0
        for root, dirs, files in os.walk(self.local_file):
            for file in files:
                if file.endswith('.csv'):
                    i += 1
                    hh.putFile(os.path.join(root, file), os.path.join(self.remote_file, str(i) + file))

        self.log.info("HdfsPutCsvOperator done.")