#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import random
import time
import traceback

from ragflow.api.db.db_models import close_connection
from ragflow.api.db.services.task_service import TaskService
from ragflow.rag.settings import cron_logger
from ragflow.rag.utils.minio_conn import MINIO
from ragflow.rag.utils.redis_conn import REDIS_CONN


def collect():
    doc_locations = TaskService.get_ongoing_doc_name()
    print(doc_locations)
    if len(doc_locations) == 0:
        time.sleep(1)
        return
    return doc_locations

def main():
    locations = collect()
    if not locations:return
    print("TASKS:", len(locations))
    for kb_id, loc in locations:
        try:
            if REDIS_CONN.is_alive():
                try:
                    key = "{}/{}".format(kb_id, loc)
                    if REDIS_CONN.exist(key):continue
                    file_bin = MINIO.get(kb_id, loc)
                    REDIS_CONN.transaction(key, file_bin, 12 * 60)
                    cron_logger.info("CACHE: {}".format(loc))
                except Exception as e:
                    traceback.print_stack(e)
        except Exception as e:
            traceback.print_stack(e)



if __name__ == "__main__":
    while True:
        main()
        close_connection()
        time.sleep(1)