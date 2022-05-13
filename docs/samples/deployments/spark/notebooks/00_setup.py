# Databricks notebook source
# MAGIC %md
# MAGIC # Mount Azure Storage blob container
# MAGIC
# MAGIC <br>Mount an Azure Storage blob container to a databricks cluster.
# MAGIC
# MAGIC <br>This sciprt requires the following environment variables to be set.
# MAGIC
# MAGIC <ol>
# MAGIC <li>STORAGE_MOUNT_NAME - Name of mount which will be used by notebooks accessing the mount point.</li>
# MAGIC <li>STORAGE_ACCOUNT_NAME - Azure Storage account name.</li>
# MAGIC <li>STORAGE_CONTAINER_NAME - Blob container name</li>
# MAGIC </ol>
# MAGIC
# MAGIC <br>Additionaly, the following secrets are used.
# MAGIC
# MAGIC <ol>
# MAGIC <li>storage_account_access_key under scope storage_scope - storage account key.</li>
# MAGIC </ol>

# COMMAND ----------

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
