"""增强版批量下载功能"""

import json
import zipfile
import tempfile
import os
import time
import traceback
from pathlib import Path
from threading import Thread
from flask import Response, send_file


def setup_enhanced_download_routes(app, api_service, APIResponse, playlist_detail):
    """设置增强的下载路由"""

    @app.route('/batch_download_v2', methods=['POST'])
    def batch_download_v2():
        """增强版批量下载 - 启动下载任务并返回任务ID"""
        try:
            # 获取请求参数
            data = api_service._safe_get_request_data()
            playlist_id = data.get('playlist_id')
            quality = data.get('quality', 'lossless')

            # 参数验证
            if not playlist_id:
                return APIResponse.error("必须提供 'playlist_id' 参数")

            # 获取歌单详情
            cookies = api_service._get_cookies()
            playlist_result = playlist_detail(playlist_id, cookies)

            if not playlist_result or 'tracks' not in playlist_result:
                return APIResponse.error("获取歌单详情失败", 404)

            tracks = playlist_result['tracks']
            max_download = int(data.get('max_download', 0))
            if max_download > 0:
                tracks = tracks[:max_download]

            if len(tracks) == 0:
                return APIResponse.error("歌单中没有歌曲", 404)

            # 生成任务ID
            task_id = api_service.progress_manager.generate_task_id()
            playlist_name = playlist_result.get('name', '未知歌单')

            # 创建下载任务
            api_service.progress_manager.create_task(task_id, len(tracks), playlist_name)

            # 启动后台下载任务
            thread = Thread(
                target=background_batch_download,
                args=(task_id, tracks, quality, playlist_name, api_service)
            )
            thread.daemon = True
            thread.start()

            return APIResponse.success({
                'task_id': task_id,
                'playlist_name': playlist_name,
                'total_tracks': len(tracks)
            }, "下载任务已启动")

        except Exception as e:
            api_service.logger.error(f"启动批量下载任务失败: {e}\\n{traceback.format_exc()}")
            return APIResponse.error(f"启动下载任务失败: {str(e)}", 500)

    @app.route('/download_progress/<task_id>')
    def download_progress_stream(task_id):
        """SSE进度推送端点"""
        def generate():
            while True:
                try:
                    progress = api_service.progress_manager.get_progress(task_id)
                    if not progress:
                        yield APIResponse.sse_message({'error': '任务不存在'})
                        break

                    yield APIResponse.sse_message(progress)

                    # 如果任务完成或失败，发送最后的状态并退出
                    if progress.get('status') in ['completed', 'failed']:
                        time.sleep(1)  # 确保客户端收到最后的状态
                        break

                    time.sleep(1)  # 每秒推送一次

                except Exception as e:
                    api_service.logger.error(f"SSE推送异常: {e}")
                    yield APIResponse.sse_message({'error': str(e)})
                    break

        return Response(generate(), mimetype='text/event-stream')

    @app.route('/download_result/<task_id>')
    def download_result(task_id):
        """获取下载结果文件"""
        try:
            progress = api_service.progress_manager.get_progress(task_id)
            if not progress:
                return APIResponse.error("任务不存在", 404)

            if progress.get('status') != 'completed':
                return APIResponse.error("任务尚未完成", 400)

            zip_path = progress.get('zip_path')
            if not zip_path or not Path(zip_path).exists():
                return APIResponse.error("下载文件不存在", 404)

            # 清理任务
            def cleanup():
                try:
                    os.unlink(zip_path)
                    api_service.progress_manager.cleanup_task(task_id)
                except:
                    pass

            playlist_name = progress.get('playlist_name', '歌单')
            safe_name = ''.join(c for c in playlist_name if c not in r'<>:"/\\|?*')[:50]
            download_name = f"{safe_name}_{progress.get('quality', 'lossless')}.zip"

            response = send_file(
                zip_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/zip'
            )

            response.call_on_close = cleanup
            return response

        except Exception as e:
            api_service.logger.error(f"获取下载结果失败: {e}")
            return APIResponse.error(f"获取下载结果失败: {str(e)}", 500)


def background_batch_download(task_id: str, tracks: list, quality: str, playlist_name: str, api_service):
    """后台批量下载函数"""
    zip_path = None
    try:
        # 更新状态为下载中
        api_service.progress_manager.update_progress(
            task_id, status='downloading', quality=quality
        )

        # 创建临时ZIP文件
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        zip_path = temp_zip.name
        temp_zip.close()

        success_count = 0
        failed_tracks = []

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, track in enumerate(tracks):
                try:
                    track_id = str(track['id'])
                    track_name = track['name']
                    artists = track.get('artists', '未知歌手')

                    # 更新当前下载状态
                    api_service.progress_manager.update_progress(
                        task_id,
                        current_index=idx + 1,
                        current_track=f"{track_name} - {artists}"
                    )

                    api_service.logger.info(f"正在下载 ({idx+1}/{len(tracks)}): {track_name} - {artists}")

                    # 下载歌曲
                    download_result = api_service.downloader.download_music_file(
                        track_id, quality
                    )

                    if download_result.success and download_result.file_path:
                        file_path = Path(download_result.file_path)
                        if file_path.exists():
                            # 生成安全的文件名
                            safe_name = f"{track_name} - {artists}"
                            safe_name = ''.join(c for c in safe_name if c not in r'<>:"/\\|?*')
                            file_ext = file_path.suffix
                            zip_filename = f"{idx+1:03d}. {safe_name}{file_ext}"

                            # 添加到ZIP文件
                            zipf.write(str(file_path), zip_filename)
                            success_count += 1

                            # 更新成功计数
                            api_service.progress_manager.update_progress(
                                task_id, success_count=success_count
                            )

                            # 删除临时文件
                            try:
                                file_path.unlink()
                            except:
                                pass
                    else:
                        failed_tracks.append({
                            'name': track_name,
                            'artists': artists,
                            'reason': download_result.error_message or '下载失败'
                        })

                except Exception as e:
                    api_service.logger.error(f"下载歌曲失败: {e}")
                    failed_tracks.append({
                        'name': track.get('name', 'Unknown'),
                        'artists': track.get('artists', 'Unknown'),
                        'reason': str(e)
                    })

                # 更新失败计数
                api_service.progress_manager.update_progress(
                    task_id, failed_count=len(failed_tracks), failed_tracks=failed_tracks
                )

            # 更新状态为打包中
            api_service.progress_manager.update_progress(
                task_id, status='packing', current_track='正在生成下载报告...'
            )

            # 添加下载报告
            report = {
                'playlist_name': playlist_name,
                'total_tracks': len(tracks),
                'success_count': success_count,
                'failed_count': len(failed_tracks),
                'failed_tracks': failed_tracks,
                'quality': quality
            }
            report_json = json.dumps(report, ensure_ascii=False, indent=2)
            zipf.writestr('download_report.json', report_json)

        if success_count > 0:
            # 任务完成
            api_service.progress_manager.update_progress(
                task_id,
                status='completed',
                zip_path=zip_path,
                current_track='下载完成！'
            )
        else:
            # 任务失败
            api_service.progress_manager.update_progress(
                task_id,
                status='failed',
                error_message='没有成功下载任何歌曲'
            )
            try:
                os.unlink(zip_path)
            except:
                pass

    except Exception as e:
        api_service.logger.error(f"批量下载异常: {e}\\n{traceback.format_exc()}")
        api_service.progress_manager.update_progress(
            task_id,
            status='failed',
            error_message=str(e)
        )
        if zip_path:
            try:
                os.unlink(zip_path)
            except:
                pass