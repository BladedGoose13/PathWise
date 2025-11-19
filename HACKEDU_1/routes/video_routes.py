from flask import Blueprint, request, jsonify
from api_integrators.video_integrator import VideoIntegrator
from api_integrators.ai_integrator import AIGenerator
from streaming.video_streamer import VideoStreamer
from cache.redis_cache import RedisCache
from utils.rate_limiter import APIRateLimiter, RateLimitException
from utils.error_handler import ErrorHandler
import hashlib

video_bp = Blueprint('video', __name__)
video_integrator = VideoIntegrator()
ai_generator = AIGenerator()
video_streamer = VideoStreamer()
cache = RedisCache()
rate_limiter = APIRateLimiter()

@video_bp.route('/api/videos/search', methods=['POST'])
@rate_limiter.rate_limit('video_search', max_calls=50, time_window=3600)
def search_videos():
    """Search for educational videos"""
    data = request.json
    topic = data.get('topic')
    max_results = data.get('max_results', 5)
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    # Check cache
    cache_key = f"videos:{hashlib.md5(topic.encode()).hexdigest()}"
    cached_results = cache.get_json(cache_key)
    
    if cached_results:
        return jsonify({
            'success': True,
            'results': cached_results,
            'from_cache': True
        })
    
    # Search videos
    try:
        results = video_integrator.search_all(topic, max_results)
        
        # Cache results for 1 hour
        cache.set_json(cache_key, results, ttl=3600)
        
        return jsonify({
            'success': True,
            'results': results,
            'from_cache': False
        })
    except RateLimitException as e:
        return jsonify({'error': str(e)}), 429
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@video_bp.route('/api/videos/generate', methods=['POST'])
@rate_limiter.rate_limit('video_generation', max_calls=10, time_window=3600)
def generate_video():
    """Generate AI video script when user dislikes all resources"""
    data = request.json
    topic = data.get('topic')
    class_name = data.get('class_name')
    duration = data.get('duration', 300)
    
    if not topic or not class_name:
        return jsonify({'error': 'Topic and class_name required'}), 400
    
    try:
        script = ai_generator.generate_video_script(topic, class_name, duration)
        
        return jsonify({
            'success': True,
            'script': script,
            'message': 'Video script generated. Video generation coming soon!'
        })
    except Exception as e:
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500

@video_bp.route('/api/videos/stream')
def stream_video():
    """Stream video through server"""
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL parameter required'}), 400
    
    return video_streamer.stream_video(video_url)
