# Databricks notebook source
import os

# Environment Variables
storage_mount_name = os.environ["STORAGE_MOUNT_NAME"]
storage_account_name = os.environ["STORAGE_ACCOUNT_NAME"]
storage_container_name = os.environ["STORAGE_CONTAINER_NAME"]
# COMMAND ----------

# Retrieve storage credentials
storage_account_access_key = dbutils.secrets.get(
    scope="storage_scope", key="storage_account_access_key"
)


# unmount container if previously mounted
def sub_unmount(str_path):
    if any(mount.mountPoint == str_path for mount in dbutils.fs.mounts()):
        dbutils.fs.unmount(str_path)


sub_unmount(storage_mount_name)
# Refresh mounts
dbutils.fs.refreshMounts()

# mount the container
dbutils.fs.mount(
    source="wasbs://"
    + storage_container_name
    + "@"
    + storage_account_name
    + ".blob.core.windows.net",
    mount_point=storage_mount_name,
    extra_configs={
        "fs.azure.account.key."
        + storage_account_name
        + ".blob.core.windows.net": storage_account_access_key
    },
)
