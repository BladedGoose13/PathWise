import requests
from fastapi.responses import StreamingResponse, Response
from typing import Generator

class VideoStreamer:
    @staticmethod
    def stream_video(video_url: str, chunk_size: int = 8192) -> Response | StreamingResponse:
        """Stream video from external URL through your server"""
        try:
            req = requests.get(video_url, stream=True, timeout=30)
            req.raise_for_status()

            def generate() -> Generator[bytes, None, None]:
                try:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:
                            yield chunk
                finally:
                    req.close()

            return StreamingResponse(
                generate(),
                media_type=req.headers.get('content-type', 'video/mp4'),
                headers={
                    'Accept-Ranges': 'bytes',
                    'Content-Length': req.headers.get('content-length'),
                    'Cache-Control': 'no-cache',
                }
            )

        except requests.exceptions.RequestException as e:
            print(f"Video streaming error: {e}")
            return Response(
                content=f"Error streaming video: {str(e)}",
                status_code=500,
                media_type="text/plain"
            )
        except Exception as e:
            print(f"Video streaming error: {e}")
            return Response(
                content="Error streaming video: Internal server error",
                status_code=500,
                media_type="text/plain"
            )