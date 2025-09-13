"""下载进度管理模块"""

import json
import uuid
from threading import Lock
from typing import Dict, Any


class DownloadProgressManager:
    """下载进度管理器"""

    def __init__(self):
        self.tasks = {}  # task_id -> progress_info
        self.lock = Lock()

    def create_task(self, task_id: str, total_count: int, playlist_name: str):
        """创建下载任务"""
        with self.lock:
            self.tasks[task_id] = {
                'task_id': task_id,
                'playlist_name': playlist_name,
                'total_count': total_count,
                'current_index': 0,
                'success_count': 0,
                'failed_count': 0,
                'current_track': '',
                'status': 'starting',  # starting, downloading, packing, completed, failed
                'error_message': '',
                'zip_path': '',
                'failed_tracks': []
            }

    def update_progress(self, task_id: str, **kwargs):
        """更新下载进度"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(kwargs)

    def get_progress(self, task_id: str):
        """获取下载进度"""
        with self.lock:
            return self.tasks.get(task_id, {})

    def cleanup_task(self, task_id: str):
        """清理任务"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]

    def generate_task_id(self) -> str:
        """生成唯一任务ID"""
        return str(uuid.uuid4())