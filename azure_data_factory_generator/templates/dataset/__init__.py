from json import dumps
from .data_lake import data_lake_folder, data_lake_file
from .sftp import sftp_folder, sftp_file

all_data_sets = {
    ds["name"]: ds
    for ds in [
        data_lake_folder, data_lake_file, 
        sftp_folder, sftp_file
    ]
}
