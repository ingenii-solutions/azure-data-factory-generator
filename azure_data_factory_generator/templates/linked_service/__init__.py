from os import lseek
from .data_lake import data_lake
from .sftp import sftp_basic_key_vault

all_linked_services = {
    ls["name"]: ls
    for ls in [data_lake, sftp_basic_key_vault]
}
